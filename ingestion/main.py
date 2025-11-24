import argparse
import os
from warc_reader import process_warc_file

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
        print(f"📂 Procesando todos los WARC en: {args.dir}")
        for fname in os.listdir(args.dir):
            if fname.endswith(".warc.gz"):
                fullpath = os.path.join(args.dir, fname)
                print(f"\n📥 Procesando: {fullpath}")
                process_warc_file(fullpath, limit=args.limit)
        return

    print("⚠️ Debes pasar --file o --dir")

if __name__ == "__main__":
    main()
