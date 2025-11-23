from warc_reader import process_warc_file

# archivo de ejemplo 
WARC_PATH = "../data/CC-MAIN-20180420081400-20180420101400-00000.warc.gz"

if __name__ == "__main__":
    print("📥 Iniciando ingesta de datos...")
    process_warc_file(WARC_PATH)
    print("✔ Ingesta finalizada.")

