import argparse
import os
from multiprocessing import Pool, cpu_count
from ingestion.warc_reader import process_warc_file

def process_single_file(args):
    filepath, limit = args
    print(f"\n📥 Procesando archivo en paralelo: {filepath}")
    process_warc_file(filepath, limit)
    return filepath

def main():
    parser = argparse.ArgumentParser(
        description="Procesador paralelo de archivos WARC de Common Crawl",
        epilog="Ejemplo: python main.py --dir ./common_crawl_data --limit 0 (ilimitado)"
    )
    parser.add_argument("--file", type=str, help="Ruta a un archivo .warc.gz específico")
    parser.add_argument("--dir", type=str, help="Ruta a directorio con archivos .warc.gz")
    parser.add_argument("--limit", type=int, default=50, 
                       help="Páginas por archivo (0 = ilimitado, útil para procesamiento masivo)")

    args = parser.parse_args()

    # Convertir limit=0 a None para procesamiento ilimitado
    limit = None if args.limit == 0 else args.limit
    
    if args.file:
        print(f"📥 Procesando archivo: {args.file}")
        print(f"⚙️ Límite: {'ILIMITADO (procesará todo el archivo)' if limit is None else f'{limit} páginas'}")
        process_warc_file(args.file, limit=limit)
        return

    
    if args.dir:
        # Validate directory exists
        if not os.path.isdir(args.dir):
            print(f"\n⚠️ El directorio especificado no existe: {args.dir}\n" \
                  f"Por favor, proporciona una ruta válida que contenga archivos .warc.gz.")
            return

        warc_files = [
            os.path.join(args.dir, f)
            for f in os.listdir(args.dir)
            if f.endswith(".warc.gz")
        ]

        print(f"📂 Encontrados {len(warc_files)} archivos WARC")
        print(f"⚙️ Límite por archivo: {'ILIMITADO' if limit is None else f'{limit} páginas'}")
        print(f"⚙️ Ejecutando procesamiento paralelo con {cpu_count()} núcleos...\n")

        with Pool(cpu_count()) as pool:
            pool.map(process_single_file, [(f, limit) for f in warc_files])

        print("\n✔ Procesamiento paralelo completado.")
        return

    print("⚠️ Debes pasar --file o --dir")

if __name__ == "__main__":
    main()
