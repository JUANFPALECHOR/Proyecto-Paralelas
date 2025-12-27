# Guión para Video de Demostración (20 minutos)

## 📹 Estructura del Video

### SECCIÓN 1: Introducción (2 minutos)

**[Pantalla: Título del proyecto]**

- ✅ Presentación del equipo (nombres e integrantes)
- ✅ Nombre del proyecto: "Análisis de Correlación: Noticias vs COLCAP"
- ✅ Curso: Infraestructuras Paralelas y Distribuidas - Universidad del Valle
- ✅ Profesor: John Sanabria

**[Pantalla: Diagrama de arquitectura]**

- ✅ Objetivo: Correlacionar noticias de Common Crawl con índice COLCAP
- ✅ Tecnologías: Docker, Kubernetes, Python, FastAPI, Streamlit
- ✅ Backends: Pandas, Multiprocessing, Dask, Spark

---

### SECCIÓN 2: Arquitectura del Sistema (3 minutos)

**[Pantalla: Mostrar estructura de carpetas]**

```powershell
tree /F Proyecto-Paralelas
```

**Explicar componentes:**

1. **Módulo de Ingesta** (`ingestion/`)
   - Procesa archivos WARC de Common Crawl
   - Limpia HTML y extrae texto estructurado
   - Genera CSV con noticias procesadas

2. **Motor de Análisis** (`analysis/`)
   - 4 backends intercambiables (Pandas, MP, Dask, Spark)
   - Extracción de características (conteo, longitud, fechas)
   - Cálculo de correlaciones (Pearson, Spearman, Rolling)

3. **API REST** (`analysis_service/`)
   - FastAPI con endpoints para correlación
   - Configuración dinámica de backend

4. **Dashboard** (`dashboard/`)
   - Streamlit para visualización interactiva
   - Carga de CSVs y configuración de parámetros

5. **Kubernetes** (`k8s/`)
   - Manifiestos para despliegue
   - HPA para escalado automático

**[Pantalla: Diagrama de flujo de datos]**
- Mostrar pipeline: WARC → Ingesta → CSV → Análisis → Correlación → Dashboard

---

### SECCIÓN 3: Demostración Local (4 minutos)

#### 3.1 Análisis con Diferentes Backends (2 min)

**[Terminal PowerShell]**

```powershell
# Mostrar datos de entrada
Get-Content data\output.csv | Select-Object -First 5
Get-Content data\colcap_sample.csv | Select-Object -First 5

# Backend 1: Pandas (baseline)
Write-Host "Ejecutando con Pandas..." -ForegroundColor Cyan
Measure-Command {
    python -m analysis.scripts.correlate_news_colcap `
        --backend pandas `
        --colcap-csv data\colcap_sample.csv `
        --out results_pandas.json
}

# Mostrar resultado
Get-Content results_pandas.json | ConvertFrom-Json | ConvertTo-Json -Depth 3

# Backend 2: Multiprocessing
Write-Host "Ejecutando con Multiprocessing (4 procesos)..." -ForegroundColor Cyan
Measure-Command {
    python -m analysis.scripts.correlate_news_colcap `
        --backend multiprocessing `
        --mp-procs 4 `
        --colcap-csv data\colcap_sample.csv `
        --out results_mp.json
}

# Backend 3: Dask
Write-Host "Ejecutando con Dask (8 particiones)..." -ForegroundColor Cyan
Measure-Command {
    python -m analysis.scripts.correlate_news_colcap `
        --backend dask `
        --dask-nparts 8 `
        --colcap-csv data\colcap_sample.csv `
        --out results_dask.json
}
```

**Puntos a resaltar:**
- ⏱️ Diferencias de tiempo entre backends
- 🔄 Paralelización en acción
- 📊 Resultados consistentes entre backends

#### 3.2 Benchmark Comparativo (2 min)

**[Terminal]**

```powershell
# Ejecutar benchmark
python -m analysis.metrics.benchmark `
    --backends pandas multiprocessing dask `
    --mp-procs 2 4 8 `
    --dask-nparts 4 8 16 `
    --colcap-csv data\colcap_sample.csv `
    --out benchmark_results.json

# Analizar resultados
$benchmark = Get-Content benchmark_results.json | ConvertFrom-Json

Write-Host "Comparación de Rendimiento:" -ForegroundColor Yellow
foreach ($result in $benchmark) {
    Write-Host "Backend: $($result.backend)"
    Write-Host "  Tiempo total: $($result.timings_sec.total)s"
    Write-Host "  Memoria delta: $([math]::Round($result.memory_bytes.delta / 1MB, 2)) MB"
}
```

**Puntos a resaltar:**
- 📈 Gráfica comparativa (preparar imagen)
- 💾 Uso de memoria
- ⚡ Speedup logrado con paralelización

---

### SECCIÓN 4: Demostración Docker (3 minutos)

#### 4.1 Construcción de Imágenes (1 min)

**[Terminal]**

```powershell
# Mostrar Dockerfiles
Get-Content analysis_service\Dockerfile
Get-Content dashboard\Dockerfile

# Construir imágenes
docker build -t analysis-service:demo -f analysis_service/Dockerfile .
docker build -t news-dashboard:demo -f dashboard/Dockerfile .

# Listar imágenes
docker images | Select-String "analysis-service|news-dashboard"
```

#### 4.2 Docker Compose (2 min)

**[Terminal]**

```powershell
# Mostrar docker-compose.yml
Get-Content docker-compose.yml

# Iniciar servicios
docker-compose up -d

# Verificar contenedores
docker-compose ps

# Ver logs
docker-compose logs analysis-api
docker-compose logs dashboard

# Probar API
Invoke-RestMethod http://localhost:8000/health
```

**[Browser]**
- Abrir http://localhost:8000/docs (Swagger UI)
- Mostrar endpoints disponibles
- Abrir http://localhost:8501 (Dashboard)
- Mostrar interfaz de usuario

```powershell
# Detener servicios
docker-compose down
```

---

### SECCIÓN 5: Demostración Kubernetes (5 minutos)

#### 5.1 Configuración del Cluster (1 min)

**[Terminal]**

```powershell
# Iniciar Minikube (o mostrar cluster existente)
minikube start --cpus=4 --memory=8192

# Verificar cluster
kubectl cluster-info
kubectl get nodes
```

#### 5.2 Despliegue (2 min)

**[Terminal]**

```powershell
# Usar script de despliegue automatizado
.\deploy_k8s.ps1 -Registry "tu-usuario" -UseMinikube

# O manual:
kubectl apply -f k8s/analysis-service.yaml
kubectl apply -f k8s/dashboard.yaml
kubectl apply -f k8s/hpa.yaml

# Verificar despliegue
kubectl get pods -w
kubectl get svc
kubectl get hpa
```

**Mostrar YAML de análisis:**
```powershell
Get-Content k8s\analysis-service.yaml
```

**Puntos a resaltar:**
- 📦 Deployments con replicas
- 🔀 Services para comunicación interna
- 📊 HPA configurado

#### 5.3 Verificación y Acceso (2 min)

**[Terminal]**

```powershell
# Port-forward para acceso
kubectl port-forward svc/analysis-service 8000:8000
kubectl port-forward svc/news-dashboard 8501:8501

# En otra terminal, probar API
Invoke-RestMethod http://localhost:8000/health
```

**[Browser]**
- Abrir http://localhost:8501
- **DEMO COMPLETA DEL DASHBOARD:**
  1. Seleccionar backend (Multiprocessing)
  2. Configurar parámetros (4 procesos, ventanas 7-14-30)
  3. Subir CSVs (output.csv y colcap_sample.csv)
  4. Ejecutar análisis
  5. Mostrar resultados (tablas de correlación)

**[Terminal - Ver logs]**

```powershell
kubectl logs -l app=analysis-service -f
```

---

### SECCIÓN 6: Escalabilidad y HPA (3 minutos)

#### 6.1 Observar Estado Inicial

**[Terminal]**

```powershell
kubectl get pods
kubectl get hpa
```

#### 6.2 Generar Carga

**[Terminal 1: Observar HPA]**

```powershell
kubectl get hpa -w
```

**[Terminal 2: Generar carga]**

```powershell
# Port forward
kubectl port-forward svc/analysis-service 8000:8000

# En Terminal 3: Stress test
while ($true) {
    Invoke-RestMethod http://localhost:8000/health
    Start-Sleep -Milliseconds 50
}
```

**[Terminal 4: Observar pods]**

```powershell
kubectl get pods -w
```

**Puntos a resaltar:**
- 📈 CPU aumentando
- 🚀 HPA creando nuevos pods automáticamente
- ⚖️ Load balancing entre pods
- 📉 Pods reduciéndose cuando carga baja

#### 6.3 Mostrar Distribución

```powershell
# Ver réplicas
kubectl get deployment analysis-service

# Ver eventos de scaling
kubectl get events --sort-by='.lastTimestamp' | Select-String "Scaled"

# Descripción del HPA
kubectl describe hpa analysis-service-hpa
```

---

### SECCIÓN 7: Resultados y Métricas (2 minutos)

**[Pantalla: Preparar slides o imágenes]**

#### 7.1 Resultados de Correlación

Mostrar visualización de:
- **Correlación Pearson global**: 0.XX
- **Correlación Spearman global**: 0.XX
- **Correlaciones Rolling (7, 14, 30 días)**: Gráfica de serie temporal

#### 7.2 Comparación de Backends

Tabla/Gráfica comparativa:

| Backend          | Tiempo (s) | Memoria (MB) | Speedup |
|------------------|------------|--------------|---------|
| Pandas           | 5.2        | 150          | 1.0x    |
| Multiprocessing  | 2.1        | 180          | 2.5x    |
| Dask             | 1.8        | 200          | 2.9x    |
| Spark            | 2.5        | 250          | 2.1x    |

**Puntos a resaltar:**
- ✅ Paralelización reduce tiempo significativamente
- ✅ Trade-off entre velocidad y memoria
- ✅ Dask mejor para este volumen de datos

#### 7.3 Escalabilidad

Mostrar:
- 📊 Gráfica de scaling (replicas vs tiempo)
- 📈 Throughput mejorado con múltiples pods
- ⚡ Respuesta rápida a cambios de carga

---

### SECCIÓN 8: Conclusiones (1 minuto)

**[Pantalla: Resumen]**

#### ✅ Logros Alcanzados

1. ✅ **Pipeline completo** de ingesta, procesamiento y análisis
2. ✅ **4 backends** de procesamiento paralelo/distribuido
3. ✅ **Arquitectura de contenedores** con Docker
4. ✅ **Orquestación con Kubernetes** con escalado automático
5. ✅ **Dashboard interactivo** para visualización
6. ✅ **Benchmarking** de rendimiento y escalabilidad

#### 🎯 Objetivos Cumplidos

- ✅ Aplicar computación paralela y distribuida
- ✅ Procesar datos de Common Crawl
- ✅ Correlacionar con indicadores económicos (COLCAP)
- ✅ Arquitectura modular y escalable
- ✅ Evaluación de desempeño

#### 💡 Aprendizajes

- Diferencias entre estrategias de paralelización
- Trade-offs entre backends (velocidad vs memoria)
- Orquestación de contenedores en producción
- Escalado automático basado en métricas
- Pipeline de procesamiento de datos reales

---

## 🎬 Checklist de Grabación

### Antes de Grabar

- [ ] Tener todos los datos listos (`output.csv`, `colcap_sample.csv`)
- [ ] Limpiar resultados anteriores (`rm *.json`)
- [ ] Cluster de Kubernetes funcionando
- [ ] Docker Desktop/Minikube iniciado
- [ ] Abrir todas las terminales necesarias
- [ ] Preparar slides con gráficas de resultados
- [ ] Probar todos los comandos previamente

### Durante la Grabación

- [ ] Mantener terminal con fuente grande (zoom)
- [ ] Limpiar pantalla regularmente (`Clear-Host`)
- [ ] Pausar para explicar resultados importantes
- [ ] Usar colores para resaltar (`Write-Host -ForegroundColor`)
- [ ] Mostrar archivos de configuración relevantes
- [ ] No apurarse - claridad sobre velocidad

### Transiciones Sugeridas

**Entre secciones:**
```powershell
Clear-Host
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SECCIÓN X: [TÍTULO]" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
```

### Comandos de Respaldo

Si algo falla, tener listos:

```powershell
# Reset Docker
docker-compose down -v
docker system prune -f

# Reset Kubernetes
kubectl delete -f k8s/
minikube delete
minikube start

# Reset datos
Copy-Item data\backup\* data\
```

---

## 📝 Notas Finales

### Lo Más Importante a Mostrar

1. ✅ **Paralelización funcionando** (diferencias de tiempo visibles)
2. ✅ **Múltiples pods en K8s** ejecutándose simultáneamente
3. ✅ **HPA escalando automáticamente** bajo carga
4. ✅ **Dashboard funcional** con resultados reales
5. ✅ **Pipeline completo** de extremo a extremo

### Evitar

- ❌ Comandos que tarden mucho (usar datos pequeños)
- ❌ Errores de tipeo (copiar de script)
- ❌ Explicaciones demasiado técnicas (mantener alto nivel)
- ❌ Quedarse atascado en detalles menores

### Tips

- ✅ Usar `Measure-Command` para mostrar tiempos
- ✅ Usar `Get-Content | ConvertFrom-Json` para formatear salidas
- ✅ Tener múltiples ventanas de terminal pre-configuradas
- ✅ Preparar comandos en archivo .txt para copy-paste rápido
- ✅ Grabar en segmentos y editar después si es necesario

---

## ⏱️ Cronograma

| Sección | Minutos | Total Acumulado |
|---------|---------|-----------------|
| 1. Introducción | 2 | 2 |
| 2. Arquitectura | 3 | 5 |
| 3. Demo Local | 4 | 9 |
| 4. Docker | 3 | 12 |
| 5. Kubernetes | 5 | 17 |
| 6. Escalabilidad | 3 | 20 |
| 7. Resultados | 2 | 22* |
| 8. Conclusiones | 1 | 23* |

*Ajustar según tiempo disponible. Priorizar secciones 5-6 (Kubernetes y HPA).

---

¡Buena suerte con la grabación! 🎥🚀
