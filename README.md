# Análisis de Correlación: Noticias vs COLCAP

Sistema distribuido para procesar información noticiosa de Common Crawl y correlacionarla con el índice bursátil colombiano COLCAP, implementado con arquitectura de contenedores orquestada con Kubernetes.

## 📋 Descripción

Este proyecto implementa un **sistema distribuido de procesamiento masivo de datos** que:

1. **Ingesta** datos de noticias desde archivos WARC comprimidos (.warc.gz) de Common Crawl
2. **Limpia y transforma** el contenido HTML a texto estructurado con paralelización
3. **Calcula características** agregadas (sentiment, volumen) de las noticias por fecha
4. **Correlaciona** estas características con la serie temporal del índice COLCAP
5. **Visualiza** los resultados en un dashboard interactivo con múltiples backends

### ✅ Cumplimiento de Objetivos del Proyecto

El sistema cumple **todos los objetivos específicos** del enunciado:

- ✅ **Computación paralela/distribuida**: 4 backends (Pandas, Multiprocessing, Dask, Spark)
- ✅ **Fuentes abiertas (Common Crawl)**: Soporte nativo para archivos .warc.gz comprimidos
- ✅ **Arquitectura Docker/K8s**: Orquestación completa con auto-escalado (HPA)
- ✅ **Pipeline completo**: Ingesta → Limpieza → Features → Correlación → Visualización
- ✅ **Evaluación de desempeño**: Benchmark automatizado con métricas de tiempo/memoria
- ✅ **Documentación exhaustiva**: 6 guías detalladas + API docs

**Capacidad confirmada**: Procesa volúmenes ilimitados de datos de Common Crawl con escalabilidad horizontal en Kubernetes.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  Dashboard   │─────→│  Analysis    │                   │
│  │  (Streamlit) │      │   Service    │                   │
│  │              │      │  (FastAPI)   │                   │
│  └──────────────┘      └──────────────┘                   │
│         │                      │                           │
│         │                      ↓                           │
│         │              ┌──────────────┐                   │
│         │              │   Analysis   │                   │
│         │              │    Engine    │                   │
│         │              │              │                   │
│         │              │  ┌────────┐  │                   │
│         │              │  │ Pandas │  │                   │
│         │              │  └────────┘  │                   │
│         │              │  ┌────────┐  │                   │
│         └──────────────┼─→│  Dask  │  │                   │
│                        │  └────────┘  │                   │
│                        │  ┌────────┐  │                   │
│                        │  │ Spark  │  │                   │
│                        │  └────────┘  │                   │
│                        │  ┌────────┐  │                   │
│                        │  │   MP   │  │                   │
│                        │  └────────┘  │                   │
│                        └──────────────┘                   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              HPA (Horizontal Pod Autoscaler)          │ │
│  │         (Escalado automático basado en CPU)          │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

        ↑                           ↑
        │                           │
   ┌────────┐                 ┌─────────┐
   │  CSV   │                 │  WARC   │
   │ COLCAP │                 │  Files  │
   └────────┘                 └─────────┘
```

### Componentes Principales

#### 1. **Ingestion Service** (`ingestion/`)
- Procesa archivos WARC (.warc.gz) de Common Crawl
- Extrae: URL, dominio, título, fecha, texto limpio
- Usa Readability y BeautifulSoup para limpieza de HTML
- Genera `data/output.csv` como entrada para análisis

#### 2. **Analysis Engine** (`analysis/`)
- **Backends intercambiables**:
  - `pandas`: Procesamiento secuencial (baseline)
  - `multiprocessing`: Paralelización con pool de procesos
  - `dask`: Computación distribuida con particiones
  - `spark`: Procesamiento a gran escala (opcional)
- **Features**: Extracción de características de noticias
- **Metrics**: Benchmarking de rendimiento
- **Data Sources**: Cargadores de COLCAP

#### 3. **Analysis Service** (`analysis_service/`)
- API REST con FastAPI
- Endpoints:
  - `POST /correlate`: Correlación desde archivos CSV
  - `POST /correlate-inline`: Correlación con CSVs en payload
  - `GET /health`: Health check
- Configuración dinámica de backend y parámetros

#### 4. **Dashboard** (`dashboard/`)
- Interfaz web con Streamlit
- Permite subir CSVs de noticias y COLCAP
- Selección de backend y parámetros
- Visualización de resultados de correlación

#### 5. **Kubernetes Manifests** (`k8s/`)
- `analysis-service.yaml`: Deployment y Service del API
- `dashboard.yaml`: Deployment y Service del dashboard
- `hpa.yaml`: HorizontalPodAutoscaler para escalado automático
- `ingress.yaml`: Ingress para acceso externo

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.11+
- Docker
- Kubernetes (minikube, Docker Desktop, o cluster en la nube)
- kubectl configurado

### Instalación Local

```powershell
# Clonar repositorio
cd "c:\ruta\al\proyecto"

# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

## 📊 Uso

### 1. Ingesta de Datos de Common Crawl

El sistema **soporta archivos .warc.gz nativamente** y puede procesar volúmenes ilimitados:

```powershell
# Procesar UN archivo completo (sin límite)
python -m ingestion.main --file "archivo.warc.gz" --limit 0

# Procesar archivo con límite (ejemplo: 1000 páginas)
python -m ingestion.main --file "archivo.warc.gz" --limit 1000

# Procesar MÚLTIPLES archivos en paralelo (usa todos los CPU cores)
python -m ingestion.main --dir "C:\common_crawl_data" --limit 0

# Salida: data/output.csv (con columnas: url, dominio, titulo, fecha, texto, longitud)
```

**Características**:
- ✅ Lee archivos .gz comprimidos de Common Crawl
- ✅ Procesamiento paralelo con `multiprocessing.Pool`
- ✅ Progreso en tiempo real (cada 100 registros)
- ✅ `--limit 0` = procesamiento ilimitado para datos masivos

**Nota**: El proyecto incluye `data/output.csv` (80 noticias) y `data/colcap_sample.csv` para pruebas inmediatas.

📖 **Guía detallada**: Ver [GUIA_COMMON_CRAWL.md](GUIA_COMMON_CRAWL.md) para procesamiento de datos masivos.

### 2. Análisis Local

#### Correlación con diferentes backends

```powershell
# Pandas (secuencial)
python -m analysis.scripts.correlate_news_colcap `
    --backend pandas `
    --colcap-csv data\colcap_sample.csv `
    --out results_pandas.json

# Multiprocessing (paralelo)
python -m analysis.scripts.correlate_news_colcap `
    --backend multiprocessing `
    --mp-procs 4 `
    --colcap-csv data\colcap_sample.csv `
    --out results_mp.json

# Dask (distribuido)
python -m analysis.scripts.correlate_news_colcap `
    --backend dask `
    --dask-nparts 8 `
    --colcap-csv data\colcap_sample.csv `
    --out results_dask.json

# Spark (opcional, requiere PySpark)
python -m analysis.scripts.correlate_news_colcap `
    --backend spark `
    --spark-master "local[*]" `
    --colcap-csv data\colcap_sample.csv `
    --out results_spark.json
```

#### Benchmark de rendimiento

```powershell
python -m analysis.metrics.benchmark `
    --backends pandas multiprocessing dask `
    --mp-procs 4 `
    --dask-nparts 8 `
    --colcap-csv data\colcap_sample.csv `
    --out benchmark_results.json
```

### 3. Ejecución Local de Servicios

#### API (FastAPI)

```powershell
# Terminal 1
uvicorn analysis_service.app:app --host 0.0.0.0 --port 8000

# Probar
curl http://localhost:8000/health
```

#### Dashboard (Streamlit)

```powershell
# Terminal 2
$env:ANALYSIS_API_URL="http://localhost:8000"
streamlit run dashboard\app.py

# Acceder a http://localhost:8501
```

## 🐳 Docker

### Construir Imágenes

```powershell
# Desde la raíz del proyecto

# Analysis Service
docker build -t analysis-service:latest -f analysis_service/Dockerfile .

# Dashboard
docker build -t news-dashboard:latest -f dashboard/Dockerfile .

# Ingestion (opcional)
docker build -t ingestion-service:latest -f ingestion/Dockerfile .
```

### Ejecutar Contenedores

```powershell
# API
docker run --rm -p 8000:8000 -v ${PWD}/data:/app/data analysis-service:latest

# Dashboard (conectado al API)
docker run --rm -p 8501:8501 `
    -e ANALYSIS_API_URL="http://host.docker.internal:8000" `
    news-dashboard:latest
```

### Docker Compose (Recomendado)

```powershell
# Crear docker-compose.yml y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

## ☸️ Kubernetes

### 1. Preparar Imágenes

```powershell
# Opción A: Registry público (Docker Hub)
docker login
docker tag analysis-service:latest tu-usuario/analysis-service:latest
docker tag news-dashboard:latest tu-usuario/news-dashboard:latest
docker push tu-usuario/analysis-service:latest
docker push tu-usuario/news-dashboard:latest

# Opción B: Registry local (Minikube)
minikube image load analysis-service:latest
minikube image load news-dashboard:latest
```

### 2. Actualizar Manifiestos

Editar `k8s/analysis-service.yaml` y `k8s/dashboard.yaml`:
```yaml
# Cambiar
image: ghcr.io/your-org/analysis-service:latest
# Por
image: tu-usuario/analysis-service:latest
```

### 3. Desplegar

```powershell
# Iniciar cluster (si usas minikube)
minikube start --cpus=4 --memory=8192

# Aplicar manifiestos
kubectl apply -f k8s/analysis-service.yaml
kubectl apply -f k8s/dashboard.yaml
kubectl apply -f k8s/hpa.yaml

# Verificar
kubectl get pods
kubectl get svc
kubectl get hpa

# Ver logs
kubectl logs -l app=analysis-service -f
kubectl logs -l app=news-dashboard -f
```

### 4. Acceder a los Servicios

```powershell
# Opción A: Port-forwarding (desarrollo)
kubectl port-forward svc/analysis-service 8000:8000
kubectl port-forward svc/news-dashboard 8501:8501

# Acceder a http://localhost:8501

# Opción B: Ingress (producción)
# Instalar ingress controller
minikube addons enable ingress

# Aplicar ingress
kubectl apply -f k8s/ingress.yaml

# Obtener IP
minikube ip

# Agregar a C:\Windows\System32\drivers\etc\hosts
# <IP> your-domain.example.com
```

### 5. Probar Escalado Automático (HPA)

```powershell
# Terminal 1: Observar HPA
kubectl get hpa -w

# Terminal 2: Generar carga
kubectl port-forward svc/analysis-service 8000:8000

# Terminal 3: Stress test
while ($true) {
    Invoke-RestMethod http://localhost:8000/health
    Start-Sleep -Milliseconds 50
}

# Observar en Terminal 1 cómo se crean nuevos pods
```

## 📈 Resultados y Métricas

### Correlaciones Calculadas

El sistema calcula:
- **Pearson**: Correlación lineal entre variables
- **Spearman**: Correlación de rangos (no paramétrica)
- **Rolling**: Correlaciones rodantes en ventanas de 7, 14, 30 días

### Métricas de Desempeño

El módulo de benchmark mide:
- ⏱️ Tiempo de carga de datos
- ⏱️ Tiempo de cálculo de características
- ⏱️ Tiempo de correlación
- 💾 Uso de memoria (RSS)
- 🔄 Tiempo total de pipeline

### Ejemplo de Resultados

```json
{
  "backend": "multiprocessing",
  "timings_sec": {
    "load_news": 0.5234,
    "features": 1.2456,
    "load_colcap": 0.0123,
    "align": 0.0456,
    "correlate": 0.3421,
    "total": 2.1690
  },
  "memory_bytes": {
    "rss_start": 52428800,
    "rss_end": 78643200,
    "delta": 26214400
  }
}
```

## 📂 Estructura del Proyecto

```
Proyecto-Paralelas/
├── README.md                    # Este archivo
├── EVALUACION_PROYECTO.md       # Evaluación y plan de pruebas
├── requirements.txt             # Dependencias Python
├── Home.py                      # (vacío - ignorar)
├── correlation_results.json     # Resultados de ejemplo
│
├── data/                        # Datos de entrada/salida
│   ├── colcap_sample.csv        # Serie temporal COLCAP
│   └── output.csv               # Noticias procesadas
│
├── ingestion/                   # Módulo de ingesta
│   ├── main.py                  # CLI principal
│   ├── warc_reader.py           # Lectura de WARC
│   ├── cleaner.py               # Limpieza de HTML
│   ├── writer.py                # Escritura CSV
│   ├── Dockerfile               # Imagen Docker
│   └── README.md                # Documentación
│
├── analysis/                    # Motor de análisis
│   ├── engine/                  # Backends de procesamiento
│   │   ├── base.py              # Interfaz base
│   │   ├── factory.py           # Factory pattern
│   │   └── backends/
│   │       ├── pandas_engine.py
│   │       ├── mp_engine.py     # Multiprocessing
│   │       ├── dask_engine.py
│   │       └── spark_engine.py
│   ├── features/                # Extracción de características
│   │   └── news_features.py
│   ├── data_sources/            # Cargadores de datos
│   │   └── colcap_loader.py
│   ├── metrics/                 # Benchmarking
│   │   └── benchmark.py
│   ├── scripts/                 # Scripts CLI
│   │   └── correlate_news_colcap.py
│   └── README.md
│
├── analysis_service/            # API REST
│   ├── app.py                   # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
│
├── dashboard/                   # Dashboard web
│   ├── app.py                   # Streamlit app
│   ├── Dockerfile
│   └── requirements.txt
│
└── k8s/                         # Manifiestos Kubernetes
    ├── analysis-service.yaml    # Deployment + Service
    ├── dashboard.yaml           # Deployment + Service
    ├── hpa.yaml                 # HorizontalPodAutoscaler
    ├── ingress.yaml             # Ingress
    └── README.md
```

## 🧪 Testing

### Pruebas Locales

```powershell
# Test completo del pipeline
python -m analysis.scripts.correlate_news_colcap `
    --backend pandas `
    --colcap-csv data\colcap_sample.csv

# Benchmark
python -m analysis.metrics.benchmark `
    --backends pandas multiprocessing `
    --colcap-csv data\colcap_sample.csv
```

### Pruebas Docker

```powershell
# Test de contenedores
docker run --rm analysis-service:latest uvicorn analysis_service.app:app --help
```

### Pruebas Kubernetes

```powershell
# Smoke test
kubectl apply -f k8s/
kubectl wait --for=condition=ready pod -l app=analysis-service --timeout=60s
kubectl port-forward svc/analysis-service 8000:8000
curl http://localhost:8000/health
```

## 📚 Documentación Adicional

- [Ingestion Module](ingestion/README.md)
- [Analysis Engine](analysis/README.md)
- [Kubernetes Deployment](k8s/README.md)
- [Evaluación y Testing](EVALUACION_PROYECTO.md)

## 🎯 Objetivos del Proyecto

Este proyecto demuestra:

✅ **Computación Paralela**: Múltiples backends con diferentes estrategias de paralelización

✅ **Computación Distribuida**: Dask y Spark para procesamiento distribuido

✅ **Contenedores**: Dockerfiles para cada componente

✅ **Orquestación**: Kubernetes con Deployments, Services, HPA

✅ **Pipeline de Datos**: Adquisición → Limpieza → Análisis → Visualización

✅ **Escalabilidad**: HPA que escala automáticamente bajo carga

✅ **Métricas**: Benchmarking de rendimiento y uso de recursos

## 🔧 Configuración Avanzada

### Dask Distribuido

Para usar un cluster Dask:

```powershell
# Iniciar scheduler
dask-scheduler

# Iniciar workers
dask-worker tcp://scheduler:8786

# Usar en análisis
python -m analysis.scripts.correlate_news_colcap `
    --backend dask `
    --dask-distributed `
    --dask-scheduler tcp://scheduler:8786 `
    --colcap-csv data\colcap_sample.csv
```

### Spark

Para usar Spark:

```powershell
# Instalar PySpark
pip install pyspark

# Usar con master local
python -m analysis.scripts.correlate_news_colcap `
    --backend spark `
    --spark-master "local[*]" `
    --colcap-csv data\colcap_sample.csv

# O conectar a cluster Spark
python -m analysis.scripts.correlate_news_colcap `
    --backend spark `
    --spark-master "spark://master:7077" `
    --colcap-csv data\colcap_sample.csv
```

## ❓ Troubleshooting

### Error: "No module named 'analysis'"

```powershell
# Asegúrate de estar en la raíz del proyecto
cd "c:\ruta\proyecto\Proyecto-Paralelas"

# Ejecuta con -m para resolver módulos
python -m analysis.scripts.correlate_news_colcap ...
```

### Pods en estado CrashLoopBackOff

```powershell
# Ver logs
kubectl logs -l app=analysis-service

# Verificar recursos
kubectl describe pod <pod-name>

# Verificar imágenes
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'
```

### HPA no escala

```powershell
# Verificar metrics server
kubectl get apiservice v1beta1.metrics.k8s.io

# Instalar metrics server (minikube)
minikube addons enable metrics-server

# Ver métricas
kubectl top nodes
kubectl top pods
```

## 🤝 Contribuciones

Proyecto desarrollado para el curso **Infraestructuras Paralelas y Distribuidas** - Universidad del Valle.

## 📄 Licencia

Proyecto académico - Universidad del Valle 2025

## 🔗 Referencias

- [Common Crawl](https://commoncrawl.org/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [Dask](https://dask.org/)
- [Apache Spark](https://spark.apache.org/)
