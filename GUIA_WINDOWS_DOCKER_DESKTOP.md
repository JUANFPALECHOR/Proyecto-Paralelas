# Guía de Pruebas: Windows + Docker Desktop

Esta guía está optimizada para probar el proyecto en **Windows con Docker Desktop**.

## 📋 Prerrequisitos

### 1. Instalar Docker Desktop

- Descargar: https://www.docker.com/products/docker-desktop/
- Versión recomendada: 4.x o superior
- Asegúrate de tener WSL 2 habilitado

### 2. Habilitar Kubernetes

1. Abrir **Docker Desktop**
2. Click en ⚙️ **Settings**
3. Ir a **Kubernetes**
4. ✅ Marcar **Enable Kubernetes**
5. Click en **Apply & Restart**
6. Esperar a que aparezca 🟢 verde en el ícono de Kubernetes

**Verificación:**
```powershell
kubectl version --client
kubectl cluster-info
kubectl get nodes
```

**Deberías ver:**
```
NAME             STATUS   ROLES           AGE   VERSION
docker-desktop   Ready    control-plane   ...   v1.xx.x
```

---

## 🚀 Guía de Pruebas Paso a Paso

### PASO 1: Configurar Entorno Python

```powershell
# Navegar al proyecto
cd "c:\Users\jjmaf\OneDrive\Documents\UNIVALLE\SEMESTRES\SEMESTRE 7\INFRAESTRCUTURA Y PARALELAS\Proyecto_Final\Proyecto-Paralelas"

# Crear entorno virtual (si no existe)
python -m venv .venv

# Activar
.\.venv\Scripts\Activate.ps1

# Si hay error de políticas, ejecutar como Admin:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar dependencias
pip install -r requirements.txt
```

---

### PASO 2: Pruebas Locales (Sin Docker)

#### 2.1. Verificar Datos

```powershell
# Ver datos de noticias
Get-Content data\output.csv | Select-Object -First 3

# Ver datos de COLCAP
Get-Content data\colcap_sample.csv | Select-Object -First 3
```

#### 2.2. Probar Backend Pandas

```powershell
python -m analysis.scripts.correlate_news_colcap `
    --backend pandas `
    --colcap-csv data\colcap_sample.csv `
    --out test_pandas.json

# Ver resultado
Get-Content test_pandas.json | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

#### 2.3. Probar Backend Multiprocessing

```powershell
python -m analysis.scripts.correlate_news_colcap `
    --backend multiprocessing `
    --mp-procs 4 `
    --colcap-csv data\colcap_sample.csv `
    --out test_mp.json

# Comparar tiempos
Write-Host "Resultados guardados en test_mp.json"
```

#### 2.4. Probar API Local

**Terminal 1: Iniciar API**
```powershell
uvicorn analysis_service.app:app --host 0.0.0.0 --port 8000
```

**Terminal 2: Probar endpoints**
```powershell
# Health check
Invoke-RestMethod http://localhost:8000/health

# Abrir Swagger UI en navegador
Start-Process "http://localhost:8000/docs"
```

#### 2.5. Probar Dashboard Local

**Terminal 3: Iniciar Dashboard**
```powershell
$env:ANALYSIS_API_URL="http://localhost:8000"
streamlit run dashboard\app.py
```

**Navegador:** http://localhost:8501
- Subir `data\output.csv` y `data\colcap_sample.csv`
- Seleccionar backend
- Ejecutar análisis

**Detener servicios:** `Ctrl+C` en cada terminal

---

### PASO 3: Pruebas con Docker (Sin Kubernetes)

#### 3.1. Construir Imágenes

```powershell
# Analysis Service
docker build -t analysis-service:test -f analysis_service/Dockerfile .

# Dashboard
docker build -t news-dashboard:test -f dashboard/Dockerfile .

# Verificar imágenes
docker images | Select-String "analysis-service|news-dashboard"
```

#### 3.2. Probar Contenedores Individualmente

**Probar API:**
```powershell
# Iniciar contenedor
docker run -d --name test-api -p 8000:8000 analysis-service:test

# Probar
Start-Sleep 5
Invoke-RestMethod http://localhost:8000/health

# Detener y limpiar
docker stop test-api
docker rm test-api
```

**Probar Dashboard:**
```powershell
# Iniciar (conectado al API del host)
docker run -d --name test-dashboard -p 8501:8501 `
    -e ANALYSIS_API_URL="http://host.docker.internal:8000" `
    news-dashboard:test

# Abrir navegador
Start-Process "http://localhost:8501"

# Detener
docker stop test-dashboard
docker rm test-dashboard
```

#### 3.3. Usar Docker Compose

```powershell
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Probar servicios
Invoke-RestMethod http://localhost:8000/health
Start-Process "http://localhost:8501"

# Detener todo
docker-compose down
```

---

### PASO 4: Despliegue en Kubernetes (Docker Desktop)

#### 4.1. Preparar Imágenes para Kubernetes

Docker Desktop usa el mismo daemon que Kubernetes, así que las imágenes ya están disponibles.

**Opción A: Usar imágenes locales (más rápido para testing)**

```powershell
# Etiquetar con nombre simple
docker tag analysis-service:test analysis-service:latest
docker tag news-dashboard:test news-dashboard:latest

# Actualizar manifiestos para usar imagePullPolicy: Never
# Esto evita que intente descargar de un registry
```

**Opción B: Publicar a Docker Hub**

```powershell
# Login
docker login

# Etiquetar con tu usuario
docker tag analysis-service:test tu-usuario/analysis-service:latest
docker tag news-dashboard:test tu-usuario/news-dashboard:latest

# Publicar
docker push tu-usuario/analysis-service:latest
docker push tu-usuario/news-dashboard:latest
```

#### 4.2. Desplegar con Script Automatizado

**Si usas imágenes locales:**

Primero edita temporalmente los manifiestos:

```powershell
# Crear copias para testing local
Copy-Item k8s\analysis-service.yaml k8s\analysis-service-local.yaml
Copy-Item k8s\dashboard.yaml k8s\dashboard-local.yaml

# Editar manualmente o con script:
$content = Get-Content k8s\analysis-service-local.yaml -Raw
$content = $content -replace 'image: .*', 'image: analysis-service:latest'
$content = $content -replace 'imagePullPolicy: IfNotPresent', 'imagePullPolicy: Never'
$content | Set-Content k8s\analysis-service-local.yaml

$content = Get-Content k8s\dashboard-local.yaml -Raw
$content = $content -replace 'image: .*', 'image: news-dashboard:latest'
$content = $content -replace 'imagePullPolicy: IfNotPresent', 'imagePullPolicy: Never'
$content | Set-Content k8s\dashboard-local.yaml

# Desplegar
kubectl apply -f k8s\analysis-service-local.yaml
kubectl apply -f k8s\dashboard-local.yaml
kubectl apply -f k8s\hpa.yaml
```

**Si usas Docker Hub:**

```powershell
.\deploy_k8s.ps1 -Registry "tu-usuario" -Tag "latest"
```

#### 4.3. Verificar Despliegue

```powershell
# Ver pods
kubectl get pods -w
# Espera a que todos estén Running

# Ver servicios
kubectl get svc

# Ver HPA
kubectl get hpa

# Ver logs
kubectl logs -l app=analysis-service --tail=50
kubectl logs -l app=news-dashboard --tail=50
```

#### 4.4. Acceder a los Servicios

**Port-Forward (Recomendado para Docker Desktop):**

**Terminal 1:**
```powershell
kubectl port-forward svc/analysis-service 8000:8000
```

**Terminal 2:**
```powershell
kubectl port-forward svc/news-dashboard 8501:8501
```

**Navegador:**
- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

---

### PASO 5: Probar Escalado Automático (HPA)

#### 5.1. Verificar Metrics Server

Docker Desktop incluye metrics-server, pero verifica:

```powershell
kubectl get apiservice v1beta1.metrics.k8s.io

# Si no está disponible, instalar:
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

#### 5.2. Ver HPA

```powershell
# Estado del HPA
kubectl get hpa

# Detalles
kubectl describe hpa analysis-service-hpa

# Ver en tiempo real
kubectl get hpa -w
```

#### 5.3. Generar Carga

**Terminal 1: Observar HPA**
```powershell
kubectl get hpa -w
```

**Terminal 2: Port-forward**
```powershell
kubectl port-forward svc/analysis-service 8000:8000
```

**Terminal 3: Generar carga**
```powershell
# Stress test simple
while ($true) {
    try {
        Invoke-RestMethod http://localhost:8000/health -Method GET
    } catch {}
    Start-Sleep -Milliseconds 50
}
```

**Terminal 4: Ver pods escalando**
```powershell
kubectl get pods -w
```

**Observa cómo:**
- CPU usage aumenta en Terminal 1
- Nuevos pods se crean en Terminal 4
- HPA escala de 1 a 2, 3, hasta maxReplicas (5)

**Detener carga:** `Ctrl+C` en Terminal 3
**Observa cómo:** Los pods se reducen automáticamente después de unos minutos

---

### PASO 6: Ejecutar Suite Completa de Pruebas

```powershell
# Script automatizado que prueba todo
.\run_tests.ps1
```

Este script:
- ✅ Verifica dependencias
- ✅ Valida datos
- ✅ Prueba todos los backends
- ✅ Ejecuta benchmark
- ✅ Construye imágenes Docker
- ✅ Prueba contenedores
- ✅ Prueba Docker Compose

**Resultados en:** `test_results\`

---

## 🎯 Demo Completa para el Video

### Secuencia Recomendada

#### 1. Demostración Local (5 min)

```powershell
# Terminal limpia
Clear-Host

Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DEMO: Análisis Local" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan

# Mostrar datos
Write-Host "`nDatos de entrada:" -ForegroundColor Yellow
Get-Content data\output.csv | Select-Object -First 3

# Benchmark
Write-Host "`nEjecutando benchmark..." -ForegroundColor Yellow
python -m analysis.metrics.benchmark `
    --backends pandas multiprocessing dask `
    --mp-procs 4 `
    --colcap-csv data\colcap_sample.csv `
    --out demo_benchmark.json

# Mostrar resultados
$results = Get-Content demo_benchmark.json | ConvertFrom-Json
Write-Host "`nResultados:" -ForegroundColor Green
foreach ($r in $results) {
    Write-Host "  $($r.backend): $($r.timings_sec.total)s" -ForegroundColor Gray
}
```

#### 2. Docker Compose (3 min)

```powershell
Clear-Host
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DEMO: Docker Compose" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan

# Iniciar
docker-compose up -d

# Esperar
Write-Host "`nEsperando servicios..." -NoNewline
Start-Sleep 10
Write-Host " ✓" -ForegroundColor Green

# Probar
Write-Host "`nProbando API..." -NoNewline
$response = Invoke-RestMethod http://localhost:8000/health
if ($response.status -eq "healthy") {
    Write-Host " ✓" -ForegroundColor Green
}

# Abrir dashboard
Start-Process "http://localhost:8501"
```

#### 3. Kubernetes (5 min)

```powershell
Clear-Host
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DEMO: Kubernetes" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan

# Verificar cluster
Write-Host "`nCluster:" -ForegroundColor Yellow
kubectl get nodes

# Desplegar (usando imágenes locales)
kubectl apply -f k8s\analysis-service-local.yaml
kubectl apply -f k8s\dashboard-local.yaml
kubectl apply -f k8s\hpa.yaml

# Esperar pods
Write-Host "`nEsperando pods..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=analysis-service --timeout=60s

# Ver estado
Write-Host "`nEstado del cluster:" -ForegroundColor Yellow
kubectl get pods,svc,hpa

# Port-forward (en terminales separadas)
Write-Host "`nPort-forwarding..." -ForegroundColor Yellow
Start-Job -ScriptBlock { kubectl port-forward svc/analysis-service 8000:8000 }
Start-Job -ScriptBlock { kubectl port-forward svc/news-dashboard 8501:8501 }

Start-Sleep 5
Start-Process "http://localhost:8501"
```

#### 4. HPA en Acción (3 min)

```powershell
# Terminal 1: Ver HPA
kubectl get hpa -w

# Terminal 2: Generar carga
kubectl port-forward svc/analysis-service 8000:8000
while ($true) { Invoke-RestMethod http://localhost:8000/health; Start-Sleep -Milliseconds 50 }

# Terminal 3: Ver pods
kubectl get pods -w

# Narrar mientras escala: 
# "Vemos cómo el HPA detecta la carga y crea nuevos pods..."
# "Ahora tenemos X pods ejecutándose..."
```

---

## 🔧 Troubleshooting Windows

### Problema: "No se puede ejecutar scripts"

```powershell
# Ejecutar como Administrador:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problema: Kubernetes no inicia en Docker Desktop

1. Settings → Kubernetes → Reset Kubernetes Cluster
2. Apply & Restart
3. Esperar 5 minutos

### Problema: Pods en ImagePullBackOff

```powershell
# Si usas imágenes locales, verificar que existen:
docker images

# Cambiar imagePullPolicy a Never en manifiestos
```

### Problema: HPA muestra "unknown" en TARGETS

```powershell
# Esperar 1-2 minutos para que metrics-server recolecte datos
kubectl top nodes
kubectl top pods

# Si no funciona, reinstalar metrics-server
```

### Problema: Puerto ya en uso

```powershell
# Ver qué usa el puerto 8000
Get-NetTCPConnection -LocalPort 8000

# Matar proceso
Stop-Process -Id <PID> -Force

# O usar puerto diferente
kubectl port-forward svc/analysis-service 8001:8000
```

---

## 📸 Capturas para el Video

Preparar capturas de:

1. ✅ Docker Desktop con Kubernetes habilitado (🟢 verde)
2. ✅ Terminal con benchmark mostrando tiempos
3. ✅ `kubectl get pods` mostrando múltiples replicas
4. ✅ Dashboard Streamlit con resultados
5. ✅ `kubectl get hpa -w` mostrando escalado
6. ✅ Gráficas de correlación

---

## ✅ Checklist de Validación

Antes de grabar el video:

- [ ] Python y pip funcionando
- [ ] Docker Desktop con Kubernetes habilitado
- [ ] Todos los backends funcionan localmente
- [ ] Imágenes Docker construidas
- [ ] Docker Compose funciona
- [ ] Pods de K8s en estado Running
- [ ] Port-forward accede a servicios
- [ ] HPA escala correctamente
- [ ] Dashboard muestra resultados

---

## 🎬 Listo para Grabar

Una vez completados todos los pasos, estás listo para:

1. Seguir `GUION_VIDEO.md`
2. Grabar en segmentos
3. Demostrar todo funcionando end-to-end

**¡Mucho éxito!** 🚀
