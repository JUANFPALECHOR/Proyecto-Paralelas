import argparse
import os
import sys
import time
from typing import List

import requests


def read_urls(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    return urls


def download_url(url: str, out_dir: str, timeout: int = 60) -> str:
    filename = os.path.basename(url)
    out_path = os.path.join(out_dir, filename)

    if os.path.exists(out_path):
        print(f"✔ Ya existe, omitiendo: {out_path}")
        return out_path

    os.makedirs(out_dir, exist_ok=True)
    print(f"⬇ Descargando: {url}")

    with requests.get(url, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0))
        downloaded = 0
        t0 = time.perf_counter()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        percent = downloaded * 100 // total
                        sys.stdout.write(f"\r   Progreso: {percent}% ({downloaded}/{total} bytes)")
                        sys.stdout.flush()
        t1 = time.perf_counter()
        print(f"\n✔ Guardado en {out_path} en {t1 - t0:.1f}s")

    return out_path


def main():
    parser = argparse.ArgumentParser(description="Descargar muestras de WARC desde Common Crawl")
    parser.add_argument("--urls-file", type=str, required=True, help="Archivo de texto con URLs de .warc.gz de Common Crawl")
    parser.add_argument("--out-dir", type=str, default=os.path.join(os.getcwd(), "warcs"), help="Directorio destino para guardar los WARC")
    parser.add_argument("--max", type=int, default=None, help="Máximo de archivos a descargar")
    parser.add_argument("--timeout", type=int, default=60, help="Tiempo de espera por petición en segundos")

    args = parser.parse_args()

    urls = read_urls(args.urls_file)
    if args.max:
        urls = urls[: args.max]

    if not urls:
        print("⚠️ No se encontraron URLs en el archivo proporcionado")
        return

    print(f"▶ Descargando {len(urls)} archivos en: {args.out_dir}")
    for u in urls:
        try:
            download_url(u, args.out_dir, timeout=args.timeout)
        except Exception as e:
            print(f"❌ Error descargando {u}: {e}")

    print("\n✔ Descargas completadas")


if __name__ == "__main__":
    main()
