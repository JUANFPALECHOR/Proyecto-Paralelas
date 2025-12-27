# 🚀 Script de Prueba: Procesamiento de Common Crawl

# Este script procesa archivos .warc.gz que hayas descargado de Common Crawl

Write-Host "`n=== PRUEBA DE PROCESAMIENTO DE COMMON CRAWL ===" -ForegroundColor Cyan
Write-Host "Este script procesara archivos .warc.gz de Common Crawl`n" -ForegroundColor Yellow

# Verificar si hay archivos .warc.gz en el directorio actual
$warcFiles = Get-ChildItem -Path . -Filter "*.warc.gz" -Recurse | Select-Object -First 1

if ($warcFiles) {
    Write-Host "[OK] Encontrado archivo WARC: $($warcFiles.Name)" -ForegroundColor Green
    $FILEPATH = $warcFiles.FullName
}
else {
    Write-Host "[INFO] No se encontraron archivos .warc.gz en el proyecto" -ForegroundColor Yellow
    Write-Host "`nOPCIONES:" -ForegroundColor Cyan
    Write-Host "  1. Descarga un archivo WARC de Common Crawl:" -ForegroundColor White
    Write-Host "     https://data.commoncrawl.org/crawl-data/index.html" -ForegroundColor Gray
    Write-Host "`n  2. O prueba con los datos de ejemplo incluidos:" -ForegroundColor White
    Write-Host "     python -m ingestion.main --file data\output.csv (ya procesado)" -ForegroundColor Gray
    Write-Host "`n  3. Especifica tu archivo manualmente:" -ForegroundColor White
    Write-Host "     python -m ingestion.main --file `"ruta\tu_archivo.warc.gz`" --limit 100" -ForegroundColor Gray
    Write-Host ""
    
    # Preguntar si quiere probar con datos de ejemplo
    $response = Read-Host "Quieres ejecutar analisis con los datos de ejemplo (80 noticias)? (s/n)"
    if ($response -eq "s" -or $response -eq "S") {
        Write-Host "`n[OK] Ejecutando analisis con datos de ejemplo..." -ForegroundColor Green
        
        # Activar entorno virtual
        if (Test-Path ".\.venv\Scripts\Activate.ps1") {
            & .\.venv\Scripts\Activate.ps1
        }
        
        # Ejecutar analisis
        python analysis\scripts\correlate_news_colcap.py --engine pandas
        
        Write-Host "`nPrueba otros backends:" -ForegroundColor Yellow
        Write-Host "  python analysis\scripts\correlate_news_colcap.py --engine multiprocessing" -ForegroundColor White
        Write-Host "  python analysis\scripts\correlate_news_colcap.py --engine dask" -ForegroundColor White
        Write-Host "`nO ejecuta el test suite completo:" -ForegroundColor Yellow
        Write-Host "  .\run_tests.ps1" -ForegroundColor White
    }
    exit 0
}

# Verificar tamaño del archivo
$fileSize = (Get-Item $FILEPATH).Length / 1MB
Write-Host "Tamaño del archivo: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green

# Activar entorno virtual si existe
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "`nActivando entorno virtual..." -ForegroundColor Green
    & $venvPath
}
else {
    Write-Host "`nNo se encontro entorno virtual, usando Python global" -ForegroundColor Yellow
}

# Preguntar limite de procesamiento
Write-Host "`nCuantas paginas quieres procesar?" -ForegroundColor Yellow
Write-Host "  0  = TODO el archivo (puede tardar varios minutos)" -ForegroundColor Gray
Write-Host "  100 = Primeras 100 paginas (prueba rapida)" -ForegroundColor Gray
Write-Host "  1000 = Primeras 1000 paginas (prueba media)" -ForegroundColor Gray
$limit = Read-Host "Ingresa el limite (default: 100)"
if ([string]::IsNullOrWhiteSpace($limit)) { $limit = 100 }

# Procesar archivo WARC
Write-Host "`nProcesando archivo WARC con limite de $limit paginas..." -ForegroundColor Green
if ($limit -eq 0) {
    Write-Host "ADVERTENCIA: Esto procesara TODO el archivo, puede tardar mucho tiempo" -ForegroundColor Yellow
    $confirm = Read-Host "Continuar? (s/n)"
    if ($confirm -ne "s" -and $confirm -ne "S") {
        Write-Host "Cancelado por el usuario" -ForegroundColor Red
        exit 0
    }
}

Write-Host ""
python -m ingestion.main --file $FILEPATH --limit $limit

# Resultados
Write-Host "`n=== RESULTADOS ===" -ForegroundColor Cyan

if (Test-Path "data\output.csv") {
    $lines = (Get-Content "data\output.csv" | Measure-Object -Line).Lines - 1
    Write-Host "[OK] Procesamiento completado" -ForegroundColor Green
    Write-Host "     Registros extraidos: $lines" -ForegroundColor Green
    Write-Host "     Archivo de salida: data\output.csv" -ForegroundColor Green
    
    # Mostrar primeras lineas
    Write-Host "`n--- Primeras 3 noticias procesadas ---" -ForegroundColor Cyan
    Import-Csv "data\output.csv" | Select-Object -First 3 | Format-Table -Wrap
}
else {
    Write-Host "[ERROR] No se genero el archivo output.csv" -ForegroundColor Red
}

# Siguiente paso: Analisis
Write-Host "`n=== SIGUIENTE PASO: ANALISIS ===" -ForegroundColor Cyan
Write-Host "Ahora puedes analizar los datos con:" -ForegroundColor Yellow
Write-Host "  python analysis\scripts\correlate_news_colcap.py --engine pandas" -ForegroundColor White
Write-Host "  python analysis\scripts\correlate_news_colcap.py --engine dask" -ForegroundColor White
Write-Host "  .\run_tests.ps1  # Test suite completo" -ForegroundColor White

Write-Host "`n=== PROCESAMIENTO MASIVO ===" -ForegroundColor Cyan
Write-Host "Para procesar archivos completos de Common Crawl:" -ForegroundColor Yellow
Write-Host "  python -m ingestion.main --file $FILEPATH --limit 0" -ForegroundColor White
Write-Host "  python -m ingestion.main --dir $DOWNLOAD_DIR --limit 0" -ForegroundColor White
Write-Host "`nVer GUIA_COMMON_CRAWL.md para mas detalles`n" -ForegroundColor Gray
