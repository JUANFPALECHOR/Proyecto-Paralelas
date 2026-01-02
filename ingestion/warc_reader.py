from warcio.archiveiterator import ArchiveIterator # Librería para leer archivos WARC
from ingestion.writer import save_row_to_csv
from ingestion.cleaner import clean_html
import gzip # me permite abrir archivos comprimidos con gzip
import tldextract # me permite extraer dominios de URLs
import os

def process_warc_file(filepath, limit=None):
    """
    Procesa archivos WARC comprimidos (.warc.gz) de Common Crawl.
    
    Args:
        filepath: Ruta al archivo .warc.gz
        limit: Número máximo de páginas a procesar (None = ilimitado para datos masivos)
    """
    count = 0
    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "output.csv")
    output_path = os.path.abspath(output_path)


    header = ["url", "dominio", "titulo", "fecha", "texto", "longitud"]

    with gzip.open(filepath, "rb") as stream:
        for record in ArchiveIterator(stream):

            if record.rec_type != "response":
                continue

            url = record.rec_headers.get_header("WARC-Target-URI")
            html = record.content_stream().read()

            if not html or not url:
                continue

            # --- limpiar contenido y extraer metadatos ---
            try:
                titulo, fecha, texto = clean_html(html)
            except:
                continue

            dominio = tldextract.extract(url).registered_domain
            longitud = len(texto)

            # Construir fila
            row = {
                "url": url,
                "dominio": dominio,
                "titulo": titulo,
                "fecha": fecha,
                "texto": texto,
                "longitud": longitud
            }

            # Guardar en CSV
            save_row_to_csv(output_path, row, header)

            count += 1
            
            # Mostrar progreso cada 100 registros
            if count % 100 == 0:
                print(f"  ⚙️ Procesados {count} registros...")
            
            # Detener si se alcanza el límite
            if limit is not None and count >= limit:
                break

    print(f"\n✔ Procesadas {count} páginas y guardadas en output.csv\n")