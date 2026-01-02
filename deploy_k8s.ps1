# Script de Despliegue Simple en Kubernetes
# Para Windows + Docker Desktop

param(
    [Parameter(Mandatory=$false)]
    [string]$Registry = "local",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild
)

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  DESPLIEGUE EN KUBERNETES - DOCKER DESKTOP" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$AnalysisImage = "analysis-service:latest"
$DashboardImage = "news-dashboard:latest"

# Verificar kubectl
Write-Host "Verificando kubectl..." -NoNewline
kubectl version --client >$null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " [OK]" -ForegroundColor Green
} else {
    Write-Host " [ERROR]" -ForegroundColor Red
    Write-Host "Error: kubectl no esta disponible" -ForegroundColor Red
    exit 1
}

# Verificar cluster
Write-Host "Verificando cluster..." -NoNewline
kubectl cluster-info >$null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " [OK]" -ForegroundColor Green
    $Context = kubectl config current-context
    Write-Host "  Contexto: $Context" -ForegroundColor Gray
} else {
    Write-Host " [ERROR]" -ForegroundColor Red
    Write-Host "Error: No hay cluster Kubernetes disponible" -ForegroundColor Red
    Write-Host "Habilita Kubernetes en Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Construccion de imagenes
if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "Construyendo imagenes..." -ForegroundColor Cyan
    
    Write-Host "  - analysis-service..." -NoNewline
    docker build -t $AnalysisImage -f analysis_service/Dockerfile . -q
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        Write-Host " [ERROR]" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "  - news-dashboard..." -NoNewline
    docker build -t $DashboardImage -f dashboard/Dockerfile . -q
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [OK]" -ForegroundColor Green
    } else {
        Write-Host " [ERROR]" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "[ADVERTENCIA] Saltando construccion de imagenes" -ForegroundColor Yellow
}

# Actualizar manifiestos para usar imagenes locales
Write-Host ""
Write-Host "Preparando manifiestos..." -ForegroundColor Cyan

$TempDir = "k8s_temp"
if (Test-Path $TempDir) {
    Remove-Item $TempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $TempDir | Out-Null

# Analysis Service
$content = Get-Content "k8s\analysis-service.yaml" -Raw
$content = $content -replace 'image: .*analysis-service.*', "image: $AnalysisImage"
$content = $content -replace 'imagePullPolicy: IfNotPresent', 'imagePullPolicy: Never'
$content | Set-Content "$TempDir\analysis-service.yaml"

# Dashboard
$content = Get-Content "k8s\dashboard.yaml" -Raw
$content = $content -replace 'image: .*dashboard.*', "image: $DashboardImage"
$content = $content -replace 'imagePullPolicy: IfNotPresent', 'imagePullPolicy: Never'
$content | Set-Content "$TempDir\dashboard.yaml"

# Copiar HPA
Copy-Item "k8s\hpa.yaml" "$TempDir\hpa.yaml"

Write-Host "[OK] Manifiestos preparados" -ForegroundColor Green

# Despliegue
Write-Host ""
Write-Host "Desplegando en Kubernetes..." -ForegroundColor Cyan

Write-Host "  - analysis-service..." -NoNewline
kubectl apply -f "$TempDir\analysis-service.yaml" >$null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " [OK]" -ForegroundColor Green
} else {
    Write-Host " [ERROR]" -ForegroundColor Red
}

Write-Host "  - dashboard..." -NoNewline
kubectl apply -f "$TempDir\dashboard.yaml" >$null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " [OK]" -ForegroundColor Green
} else {
    Write-Host " [ERROR]" -ForegroundColor Red
}

Write-Host "  - hpa..." -NoNewline
kubectl apply -f "$TempDir\hpa.yaml" >$null 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " [OK]" -ForegroundColor Green
} else {
    Write-Host " [ERROR]" -ForegroundColor Red
}

# Limpiar
Remove-Item $TempDir -Recurse -Force

# Verificacion
Write-Host ""
Write-Host "Esperando pods..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Estado de recursos:" -ForegroundColor Yellow
Write-Host ""

Write-Host "Pods:" -ForegroundColor Gray
kubectl get pods -l app=analysis-service -o wide
kubectl get pods -l app=news-dashboard -o wide

Write-Host ""
Write-Host "Services:" -ForegroundColor Gray
kubectl get svc analysis-service dashboard

Write-Host ""
Write-Host "HPA:" -ForegroundColor Gray
kubectl get hpa

# Instrucciones
Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  DESPLIEGUE COMPLETADO" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para acceder a los servicios:" -ForegroundColor Yellow
Write-Host ""
Write-Host "# En una terminal:" -ForegroundColor Gray
Write-Host "kubectl port-forward svc/analysis-service 8000:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "# En otra terminal:" -ForegroundColor Gray
Write-Host "kubectl port-forward svc/dashboard 8501:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Luego accede a:" -ForegroundColor Yellow
Write-Host "  - API: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "  - Dashboard: http://localhost:8501" -ForegroundColor Gray
Write-Host ""
Write-Host "Para eliminar el despliegue:" -ForegroundColor Yellow
Write-Host "kubectl delete deployment analysis-service dashboard" -ForegroundColor Cyan
Write-Host "kubectl delete svc analysis-service dashboard" -ForegroundColor Cyan
Write-Host "kubectl delete hpa analysis-service-hpa" -ForegroundColor Cyan
Write-Host ""
