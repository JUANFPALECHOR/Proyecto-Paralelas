# 📦 Guía Rápida: Usar Archivos Reales de Common Crawl

## 🎯 Proceso Completo

### 1️⃣ Obtener URLs de Archivos WARC

El archivo que descargaste (`segment.paths.gz`) contiene **rutas a archivos WARC**, no los datos.

```powershell
# Ver contenido del índice
$content = Get-Content "C:\Users\jjmaf\Downloads\segment.paths.gz" -Raw | 
    ForEach-Object { [System.IO.Compression.GZipStream]::new(
        [System.IO.MemoryStream]::new([System.Text.Encoding]::UTF8.GetBytes($_)), 
        [System.IO.Compression.CompressionMode]::Decompress
    )}

# O con 7-Zip/WinRAR: Click derecho → Extraer
```

### 2️⃣ Descargar Archivos WARC Reales

Las rutas dentro de `segment.paths.gz` son relativas. Agrégales el prefijo:

```
https://data.commoncrawl.org/
```

**Ejemplo de URL completa**:
```
https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-10/segments/1707947474440.42/warc/CC-MAIN-20240215171826-20240215201826-00000.warc.gz
```

**Descargar con PowerShell**:
```powershell
# Descargar UN archivo WARC (pueden ser >1GB cada uno)
$url = "https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-10/segments/.../warc/CC-MAIN-xxx.warc.gz"
$output = "C:\common_crawl\archivo.warc.gz"
Invoke-WebRequest -Uri $url -OutFile $output
```

**Descargar con curl** (más rápido):
```powershell
curl -o "C:\common_crawl\archivo.warc.gz" "https://data.commoncrawl.org/..."
```

### 3️⃣ Procesar Archivos WARC

Una vez descargado el archivo `.warc.gz`:

```powershell
# Procesar UN archivo con límite de 100 páginas
python -m ingestion.main --file "C:\common_crawl\archivo.warc.gz" --limit 100

# Procesar SIN límite (todo el archivo - puede tardar horas)
python -m ingestion.main --file "C:\common_crawl\archivo.warc.gz" --limit 0

# Procesar MÚLTIPLES archivos en paralelo
python -m ingestion.main --dir "C:\common_crawl" --limit 500
```

### 4️⃣ Verificar Resultados

```powershell
# Ver cuántas noticias se extrajeron
$count = (Import-Csv data\output.csv | Measure-Object).Count
Write-Host "Noticias procesadas: $count"

# Ver primeras 5 noticias
Import-Csv data\output.csv | Select-Object -First 5 | Format-Table -Wrap
```

### 5️⃣ Ejecutar Análisis

```powershell
# Análisis con diferentes backends
python analysis\scripts\correlate_news_colcap.py --engine pandas
python analysis\scripts\correlate_news_colcap.py --engine multiprocessing
python analysis\scripts\correlate_news_colcap.py --engine dask

# Benchmark completo
python -m analysis.metrics.benchmark `
    --backends pandas multiprocessing dask `
    --colcap-csv data\colcap_sample.csv `
    --out benchmark_nuevos_datos.json
```

---

## 📊 Recomendaciones según Tamaño

| Tamaño Archivo WARC | Límite Recomendado | Tiempo Estimado | Noticias Esperadas |
|---------------------|-------------------|-----------------|-------------------|
| 100 MB | 100-500 | 2-5 min | 100-500 |
| 500 MB | 500-1000 | 10-20 min | 500-1000 |
| 1 GB+ | 1000-5000 | 30-60 min | 1000-5000 |
| Sin límite | 0 | 1-4 horas | Todas (miles) |

---

## ⚡ Procesamiento Rápido para Demostración

Si necesitas datos para **demostración inmediata**:

```powershell
# 1. Descarga UN archivo WARC pequeño (~100MB)
# 2. Procesa solo 200 páginas (rápido, ~3 minutos)
python -m ingestion.main --file "archivo.warc.gz" --limit 200

# 3. Ejecuta test suite
.\run_tests.ps1
```

---

## 🔧 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'warc_reader'"

**Solución**: Ya está arreglado. Ejecuta desde la raíz del proyecto:
```powershell
python -m ingestion.main --file ...
```

### Error: "El archivo no es un WARC válido"

**Causa**: Descargaste un índice (`.paths.gz`) en lugar de un archivo WARC.

**Solución**: Los archivos procesables tienen nombres como:
- ✅ `CC-MAIN-20240215171826-20240215201826-00000.warc.gz`
- ❌ `segment.paths.gz` (es un índice)
- ❌ `cc-index.paths.gz` (es un índice)

### Archivo muy grande / se demora mucho

**Solución**: Usa el parámetro `--limit` para procesar solo una muestra:
```powershell
python -m ingestion.main --file "archivo.warc.gz" --limit 500
```

### No se extraen noticias / Output vacío

**Causa**: Los archivos WARC contienen todo tipo de páginas web (no solo noticias).

**Solución**: 
- Aumenta el límite: `--limit 1000` 
- El cleaner filtra páginas que no tienen contenido útil
- Es normal que de 1000 páginas procesadas solo ~100-300 sean noticias útiles

---

## 🎥 Para tu Video de Demostración

### Opción A: Datos de Ejemplo (Rápido - Ya Listos)
```powershell
# Ya tienes 80 noticias procesadas
.\run_tests.ps1  # Muestra todos los backends funcionando
```

### Opción B: Common Crawl Real (Impresionante - Requiere Descarga)
```powershell
# 1. Descarga archivo WARC (~5 minutos)
curl -o warc.gz "https://data.commoncrawl.org/crawl-data/..."

# 2. Procesa con límite para demo (~3 minutos)
python -m ingestion.main --file warc.gz --limit 300

# 3. Muestra análisis paralelo
.\run_tests.ps1
```

---

## 📝 Notas Importantes

1. **Archivos WARC son GRANDES**: Típicamente 100MB-1GB cada uno
2. **Procesamiento puede tardar**: Sin límite puede tomar horas
3. **No todas las páginas son noticias**: De 1000 páginas, ~20-30% son útiles
4. **Usa `--limit` para pruebas**: Límite de 100-500 es suficiente para demo
5. **El sistema funciona**: Ya está probado con datos de ejemplo

---

## ✅ Checklist antes de la Presentación

- [ ] Dashboard funcionando (http://localhost:8501)
- [ ] API funcionando (http://localhost:8000/docs)
- [ ] Kubernetes deployado (`kubectl get all`)
- [ ] Datos procesados en `data/output.csv` (min 50 registros)
- [ ] Test suite pasa (`.\run_tests.ps1`)
- [ ] Benchmark generado (`benchmark_results.json`)

**Tu sistema YA cumple todos los objetivos del proyecto, con o sin Common Crawl adicional.**

---

## 🚀 Comando Final Recomendado

Para **impresionar en la presentación** sin depender de descargas:

```powershell
# Usa los 80 registros que ya tienes y demuestra:
.\run_tests.ps1  # Muestra 3 backends + Docker + K8s

# Dashboard interactivo
# Abrir navegador en: http://localhost:8501
```

**Esto es suficiente para demostrar todos los conceptos del proyecto.**
