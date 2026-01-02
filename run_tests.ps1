# Script de Pruebas Completas del Proyecto
# Ejecutar desde la raiz del proyecto

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  PRUEBAS COMPLETAS - PROYECTO PARALELAS" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$ProjectRoot = $PSScriptRoot
$DataDir = Join-Path $ProjectRoot "data"
$OutputDir = Join-Path $ProjectRoot "test_results"

# Python ejecutable (usar venv si existe)
$PythonExe = "python"
$VenvPath = Join-Path (Split-Path $ProjectRoot -Parent) ".venv\Scripts\python.exe"
if (Test-Path $VenvPath) {
    $PythonExe = $VenvPath
    Write-Host "[INFO] Usando entorno virtual: $VenvPath" -ForegroundColor Cyan
}

# Crear directorio de resultados
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Funcion para imprimir seccion
function Write-Section {
    param($Title)
    Write-Host ""
    Write-Host "---------------------------------------------------" -ForegroundColor Yellow
    Write-Host "  $Title" -ForegroundColor Yellow
    Write-Host "---------------------------------------------------" -ForegroundColor Yellow
}

# Funcion para verificar exito
function Test-Success {
    param($Message)
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $Message" -ForegroundColor Green
        return $true
    } else {
        Write-Host "[ERROR] $Message" -ForegroundColor Red
        return $false
    }
}

# ==================================================================
# FASE 1: VERIFICACION DE DEPENDENCIAS
# ==================================================================
Write-Section "FASE 1: Verificando Dependencias"

Write-Host "Verificando Python..." -ForegroundColor Cyan
python --version
Test-Success "Python instalado"

Write-Host "Verificando Docker..." -ForegroundColor Cyan
docker --version
Test-Success "Docker instalado"

Write-Host "Verificando kubectl..." -ForegroundColor Cyan
kubectl version --client 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] kubectl instalado" -ForegroundColor Green
} else {
    Write-Host "[ADVERTENCIA] kubectl no encontrado (opcional para pruebas locales)" -ForegroundColor Yellow
}

# ==================================================================
# FASE 2: VERIFICACION DE ARCHIVOS DE DATOS
# ==================================================================
Write-Section "FASE 2: Verificando Datos"

$NewsCSV = Join-Path $DataDir "output.csv"
$ColcapCSV = Join-Path $DataDir "colcap_sample.csv"

if (Test-Path $NewsCSV) {
    $NewsLines = (Get-Content $NewsCSV | Measure-Object -Line).Lines
    Write-Host "[OK] Archivo de noticias encontrado: $NewsLines lineas" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Archivo de noticias no encontrado: $NewsCSV" -ForegroundColor Red
    exit 1
}

if (Test-Path $ColcapCSV) {
    $ColcapLines = (Get-Content $ColcapCSV | Measure-Object -Line).Lines
    Write-Host "[OK] Archivo COLCAP encontrado: $ColcapLines lineas" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Archivo COLCAP no encontrado: $ColcapCSV" -ForegroundColor Red
    exit 1
}

# ==================================================================
# FASE 3: PRUEBAS DE ANALISIS LOCAL
# ==================================================================
Write-Section "FASE 3: Pruebas de Analisis (Backends)"

# Test 1: Pandas (baseline)
Write-Host ""
Write-Host "TEST 1/4: Backend Pandas..." -ForegroundColor Cyan
$OutputFile = Join-Path $OutputDir "test_pandas.json"
& $PythonExe -m analysis.scripts.correlate_news_colcap `
    --backend pandas `
    --colcap-csv $ColcapCSV `
    --out $OutputFile 2>&1 | Out-Null

if (Test-Path $OutputFile) {
    $Result = Get-Content $OutputFile | ConvertFrom-Json
    if ($Result.pearson) {
        Write-Host "[OK] Pandas: Correlacion calculada exitosamente" -ForegroundColor Green
        Write-Host "  Pearson: $($Result.pearson.global)" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Pandas: Resultado invalido" -ForegroundColor Red
    }
} else {
    Write-Host "[ERROR] Pandas: Fallo la ejecucion" -ForegroundColor Red
}

# Test 2: Multiprocessing
Write-Host ""
Write-Host "TEST 2/4: Backend Multiprocessing..." -ForegroundColor Cyan
$OutputFile = Join-Path $OutputDir "test_mp.json"
& $PythonExe -m analysis.scripts.correlate_news_colcap `
    --backend multiprocessing `
    --mp-procs 2 `
    --colcap-csv $ColcapCSV `
    --out $OutputFile 2>&1 | Out-Null

if (Test-Path $OutputFile) {
    $Result = Get-Content $OutputFile | ConvertFrom-Json
    if ($Result.pearson) {
        Write-Host "[OK] Multiprocessing: Correlacion calculada exitosamente" -ForegroundColor Green
        Write-Host "  Pearson: $($Result.pearson.global)" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Multiprocessing: Resultado invalido" -ForegroundColor Red
    }
} else {
    Write-Host "[ERROR] Multiprocessing: Fallo la ejecucion" -ForegroundColor Red
}

# Test 3: Dask
Write-Host ""
Write-Host "TEST 3/4: Backend Dask..." -ForegroundColor Cyan
$OutputFile = Join-Path $OutputDir "test_dask.json"
& $PythonExe -m analysis.scripts.correlate_news_colcap `
    --backend dask `
    --dask-nparts 4 `
    --colcap-csv $ColcapCSV `
    --out $OutputFile 2>&1 | Out-Null

if (Test-Path $OutputFile) {
    $Result = Get-Content $OutputFile | ConvertFrom-Json
    if ($Result.pearson) {
        Write-Host "[OK] Dask: Correlacion calculada exitosamente" -ForegroundColor Green
        Write-Host "  Pearson: $($Result.pearson.global)" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Dask: Resultado invalido" -ForegroundColor Red
    }
} else {
    Write-Host "[ERROR] Dask: Fallo la ejecucion" -ForegroundColor Red
}

# Test 4: Benchmark comparativo
Write-Host ""
Write-Host "TEST 4/4: Benchmark Comparativo..." -ForegroundColor Cyan
$OutputFile = Join-Path $OutputDir "benchmark.json"
& $PythonExe -m analysis.metrics.benchmark `
    --backends pandas multiprocessing dask `
    --mp-procs 2 `
    --dask-nparts 4 `
    --colcap-csv $ColcapCSV `
    --out $OutputFile 2>&1 | Out-Null

if (Test-Path $OutputFile) {
    Write-Host "[OK] Benchmark completado" -ForegroundColor Green
    $Benchmark = Get-Content $OutputFile | ConvertFrom-Json
    Write-Host ""
    Write-Host "  Resultados de Benchmark:" -ForegroundColor Gray
    Write-Host "  -------------------------" -ForegroundColor Gray
    foreach ($Result in $Benchmark) {
        Write-Host "  $($Result.backend): $($Result.timings_sec.total)s" -ForegroundColor Gray
    }
} else {
    Write-Host "[ERROR] Benchmark: Fallo la ejecucion" -ForegroundColor Red
}

# ==================================================================
# FASE 4: PRUEBAS DE DOCKER
# ==================================================================
Write-Section "FASE 4: Pruebas de Docker"

Write-Host "Construyendo imagenes Docker..." -ForegroundColor Cyan

# Build analysis-service
Write-Host "  - analysis-service..." -NoNewline
docker build -t analysis-service:test -f analysis_service/Dockerfile . -q
if ($LASTEXITCODE -eq 0) {
    Write-Host " [OK]" -ForegroundColor Green
} else {
    Write-Host " [ERROR]" -ForegroundColor Red
}

# Build dashboard
Write-Host "  - news-dashboard..." -NoNewline
docker build -t news-dashboard:test -f dashboard/Dockerfile . -q
if ($LASTEXITCODE -eq 0) {
    Write-Host " [OK]" -ForegroundColor Green
} else {
    Write-Host " [ERROR]" -ForegroundColor Red
}

Write-Host ""
Write-Host "Probando contenedor analysis-service..." -ForegroundColor Cyan
$ContainerID = docker run -d -p 8000:8000 analysis-service:test
Start-Sleep -Seconds 3

try {
    $Response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    if ($Response.status -eq "healthy") {
        Write-Host "[OK] API respondiendo correctamente" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] API respuesta inesperada" -ForegroundColor Red
    }
} catch {
    Write-Host "[ERROR] API no responde" -ForegroundColor Red
} finally {
    docker stop $ContainerID 2>&1 | Out-Null
    docker rm $ContainerID 2>&1 | Out-Null
}

# ==================================================================
# FASE 5: PRUEBAS DE DOCKER COMPOSE
# ==================================================================
Write-Section "FASE 5: Pruebas de Docker Compose"

if (Test-Path "docker-compose.yml") {
    Write-Host "Iniciando servicios con docker-compose..." -ForegroundColor Cyan
    docker-compose up -d 2>&1 | Out-Null
    
    Write-Host "Esperando servicios..." -NoNewline
    Start-Sleep -Seconds 10
    Write-Host " [OK]" -ForegroundColor Green
    
    # Test API
    try {
        $Response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
        if ($Response.status -eq "healthy") {
            Write-Host "[OK] API (compose) respondiendo" -ForegroundColor Green
        }
    } catch {
        Write-Host "[ERROR] API (compose) no responde" -ForegroundColor Red
    }
    
    # Test Dashboard
    try {
        $Response = Invoke-WebRequest -Uri "http://localhost:8501" -TimeoutSec 5 -UseBasicParsing
        if ($Response.StatusCode -eq 200) {
            Write-Host "[OK] Dashboard (compose) respondiendo" -ForegroundColor Green
        }
    } catch {
        Write-Host "[ERROR] Dashboard (compose) no responde" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "Deteniendo servicios..." -ForegroundColor Cyan
    docker-compose down 2>&1 | Out-Null
    Write-Host "[OK] Servicios detenidos" -ForegroundColor Green
} else {
    Write-Host "[ADVERTENCIA] docker-compose.yml no encontrado" -ForegroundColor Yellow
}

# ==================================================================
# RESUMEN FINAL
# ==================================================================
Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  RESUMEN DE PRUEBAS" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resultados guardados en: $OutputDir" -ForegroundColor Gray
Write-Host ""
Write-Host "Archivos generados:" -ForegroundColor Gray
Get-ChildItem $OutputDir | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Gray
}
Write-Host ""
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "PRUEBAS COMPLETADAS" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Revisar resultados en $OutputDir" -ForegroundColor Gray
Write-Host "  2. Publicar imagenes Docker" -ForegroundColor Gray
Write-Host "  3. Desplegar en Kubernetes" -ForegroundColor Gray
Write-Host "  4. Grabar video de demostracion" -ForegroundColor Gray
Write-Host ""
