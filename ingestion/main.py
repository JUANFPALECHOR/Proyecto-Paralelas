from warc_reader import process_warc_file

# archivo de ejemplo 
WARC_PATH = "../data/sample.warc.gz"

if __name__ == "__main__":
    print("📥 Iniciando ingesta de datos...")
    process_warc_file(WARC_PATH)
    print("✔ Ingesta finalizada.")

