import argparse
import os
from multiprocessing import Pool, cpu_count
from warc_reader import process_warc_file

def process_single_file(args):
    filepath, limit = args
    print(f"\n📥 Procesando archivo en paralelo: {filepath}")
    process_warc_file(filepath, limit)
    return filepath

def main():
    parser = argparse.ArgumentParser(description="Procesador de archivos WARC")
    parser.add_argument("--file", type=str, help="Ruta a un archivo WARC específico")
    parser.add_argument("--dir", type=str, help="Ruta a un directorio con varios archivos WARC")
    parser.add_argument("--limit", type=int, default=50, help="Número de páginas por archivo")

    args = parser.parse_args()

    
    if args.file:
        print(f"📥 Procesando archivo: {args.file}")
        process_warc_file(args.file, limit=args.limit)
        return

    
    if args.dir:
        warc_files = [
            os.path.join(args.dir, f)
            for f in os.listdir(args.dir)
            if f.endswith(".warc.gz")
        ]

        print(f"📂 Encontrados {len(warc_files)} archivos WARC")
        print(f"⚙️ Ejecutando procesamiento paralelo con {cpu_count()} núcleos...\n")

        with Pool(cpu_count()) as pool:
            pool.map(process_single_file, [(f, args.limit) for f in warc_files])

        print("\n✔ Procesamiento paralelo completado.")
        return

    print("⚠️ Debes pasar --file o --dir")

if __name__ == "__main__":
    main()
