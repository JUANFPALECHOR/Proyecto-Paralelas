# Despliegue en Kubernetes

Este módulo define manifiestos para desplegar el servicio de análisis (FastAPI) y el dashboard (Streamlit) en Kubernetes, con Ingress y HPA.

## Prerrequisitos
- Cluster Kubernetes con `kubectl` configurado
- Ingress Controller (e.g., NGINX)
- Metrics Server para HPA
- Registro de contenedores accesible (e.g., GHCR, Docker Hub)

## Construir y publicar imágenes

Reemplaza `your-org` y registra con tus credenciales.

```powershell
# En el directorio del proyecto
cd "C:\Users\Windows 11\Desktop\PFParalelas\Proyecto-Paralelas"

# Build imágenes
docker build -t ghcr.io/your-org/analysis-service:latest -f analysis_service/Dockerfile .
docker build -t ghcr.io/your-org/news-dashboard:latest -f dashboard/Dockerfile .

# Login y push
docker login ghcr.io
docker push ghcr.io/your-org/analysis-service:latest
docker push ghcr.io/your-org/news-dashboard:latest
```

## Despliegue

Edita `k8s/ingress.yaml` para usar tu dominio (`host`). Luego:

```powershell
kubectl apply -f k8s/analysis-service.yaml
kubectl apply -f k8s/dashboard.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Verifica
kubectl get pods,svc,ingress,hpa
```

## Acceso
- Dashboard: `https://your-domain.example.com/`
- API: `https://your-domain.example.com/api/...`

El dashboard se comunica con la API a través del Service interno `analysis-service` (configurado en la variable de entorno `ANALYSIS_API_URL`).

## Notas
- Para datos reales, monta volúmenes con CSVs o usa URLs accesibles públicamente (el endpoint `/correlate-inline` permite enviar CSVs directamente).
- Ajusta recursos (requests/limits) según la carga.
- Para Dask/Spark, considera añadir sus propios despliegues (scheduler/workers) y configurar la API con `--dask-scheduler` o `--spark-master`.
