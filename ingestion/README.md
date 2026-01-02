# Módulo de Ingesta de Datos

Este módulo se encarga de la adquisición y transformación inicial de datos provenientes de archivos WARC (`.warc.gz`).  
Permite procesar uno o varios archivos, extraer información útil y generar un archivo CSV estructurado para etapas posteriores del pipeline.

---

## 🚀 Funcionalidades principales

- Lectura de archivos WARC comprimidos (`.warc.gz`)
- Extracción de:
  - URL de la página
  - Dominio
  - Título (si existe)
  - Fecha aproximada detectada en el contenido
  - Texto limpio del cuerpo principal
  - Longitud del texto
- Limpieza del HTML usando Readability y BeautifulSoup
- Manejo robusto de errores y contenido HTML irregular
- Procesamiento de un archivo o una carpeta completa
- Escritura de los resultados en un archivo CSV (`output.csv`)
- Límite configurable de páginas por archivo para trabajar con datasets grandes

---

## 📂 Estructura del módulo

ingestion/
│── main.py
│── warc_reader.py
│── cleaner.py
│── writer.py
│── requirements.txt
│── Dockerfile


---

## 🧪 Ejecución

### Procesar un solo archivo WARC (Windows PowerShell)

```powershell
& "C:\Users\Windows 11\Desktop\PFParalelas\.venv\Scripts\python.exe" "C:\Users\Windows 11\Desktop\PFParalelas\Proyecto-Paralelas\ingestion\main.py" --file "C:\ruta\a\archivo.warc.gz" --limit 20
```

### Procesar todos los WARC de un directorio

```powershell
& "C:\Users\Windows 11\Desktop\PFParalelas\.venv\Scripts\python.exe" "C:\Users\Windows 11\Desktop\PFParalelas\Proyecto-Paralelas\ingestion\main.py" --dir "C:\ruta\a\carpeta_warc" --limit 30
```

Parámetros disponibles:

- `--file`: Procesa un archivo WARC individual
- `--dir`: Procesa todos los WARC contenidos en un directorio
- `--limit`: Número de páginas a procesar por archivo (por defecto: 50)

📤 Salida generada

El módulo produce:

data/output.csv

Con las columnas:

url
dominio
titulo
fecha
texto
longitud

Este archivo sirve como entrada para las etapas posteriores del análisis distribuido.

🛠 Requerimientos

Instala todas las dependencias desde el `requirements.txt` en la raíz del proyecto:

```powershell
cd "C:\Users\Windows 11\Desktop\PFParalelas\Proyecto-Paralelas"
& "C:\Users\Windows 11\Desktop\PFParalelas\.venv\Scripts\python.exe" -m pip install -r requirements.txt
```

🐳 Docker

Construir la imagen (desde la raíz del repo, usando el `requirements.txt` unificado):

```powershell
cd "C:\Users\Windows 11\Desktop\PFParalelas\Proyecto-Paralelas"
docker build -t ingestion-service -f ingestion/Dockerfile .
```

Ejecutar el contenedor:

```powershell
docker run --rm ingestion-service
```

---

## 📥 Descargar WARC de Common Crawl

Este proyecto incluye un script para descargar archivos WARC a partir de una lista de URLs públicas de Common Crawl:

1. Crea un archivo de texto `warc_urls.txt` con una URL por línea (tomadas de https://data.commoncrawl.org en el crawl que necesites).
2. Ejecuta el downloader:

```powershell
& "C:\Users\Windows 11\Desktop\PFParalelas\.venv\Scripts\python.exe" "C:\Users\Windows 11\Desktop\PFParalelas\Proyecto-Paralelas\ingestion\download_cc.py" --urls-file "C:\Users\Windows 11\Desktop\PFParalelas\Proyecto-Paralelas\warc_urls.txt" --out-dir "C:\Users\Windows 11\Desktop\PFParalelas\warcs" --max 3
```

Luego procesa el directorio descargado:

```powershell
& "C:\Users\Windows 11\Desktop\PFParalelas\.venv\Scripts\python.exe" "C:\Users\Windows 11\Desktop\PFParalelas\Proyecto-Paralelas\ingestion\main.py" --dir "C:\Users\Windows 11\Desktop\PFParalelas\warcs" --limit 50
```

Nota: Common Crawl es un dataset abierto; revisa el tamaño de los archivos y tu conexión antes de descargar grandes volúmenes.

