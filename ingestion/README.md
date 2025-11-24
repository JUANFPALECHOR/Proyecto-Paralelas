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

### Procesar un solo archivo WARC

```bash
python3 main.py --file ../data/warcs/archivo.warc.gz --limit 20


Procesar todos los WARC de un directorio
python3 main.py --dir ../data/warcs --limit 30

Parámetros disponibles
Parámetro	Descripción
--file	Procesa un archivo WARC individual
--dir	Procesa todos los WARC contenidos en un directorio
--limit	Número de páginas a procesar por archivo (por defecto: 50)

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

Instalar dependencias desde el archivo requirements.txt:

pip install -r requirements.txt

🐳 Docker

Construir la imagen:

docker build -t ingestion-service .

Ejecutar el contenedor:

docker run ingestion-service

