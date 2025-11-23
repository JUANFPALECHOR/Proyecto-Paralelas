from warcio.archiveiterator import ArchiveIterator # Librería para leer archivos WARC
from cleaner import clean_html
import gzip # me permite abrir archivos comprimidos con gzip

def process_warc_file(filepath, limit=50):
    count = 0
    
    with gzip.open(filepath, "rb") as stream:
        for record in ArchiveIterator(stream):

            if record.rec_type != "response":
                continue

            url = record.rec_headers.get_header("WARC-Target-URI")
            html = record.content_stream().read()
            
            if not html:
                continue

            try:
                text = clean_html(html)
            except:
                continue

            print(f"\nURL: {url}")
            print(f"Texto limpio: {text[:200]}...\n")
            
            count += 1
            if count >= limit:
                break
            
    print(f"\n✔ Procesadas {count} páginas del archivo\n")

