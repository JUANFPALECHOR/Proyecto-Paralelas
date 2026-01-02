from bs4 import BeautifulSoup
from readability import Document
import re

def clean_html(html_bytes):
    html = html_bytes.decode("utf-8", errors="ignore")

    # --- EXTRAER TÍTULO ---
    soup = BeautifulSoup(html, "lxml")
    titulo = soup.title.string.strip() if soup.title else ""

    # --- EXTRAER FECHA ---
    # Buscar fechas típicas en el texto
    fecha = ""
    patrones_fecha = [
        r"\b\d{4}-\d{2}-\d{2}\b",            # 2023-05-20
        r"\b\d{2}/\d{2}/\d{4}\b",            # 20/05/2023
        r"\b\d{1,2} de [A-Za-z]+ de \d{4}\b" # 20 de mayo de 2023
    ]

    texto_bruto = soup.get_text(" ", strip=True)

    for patron in patrones_fecha:
        match = re.search(patron, texto_bruto)
        if match:
            fecha = match.group(0)
            break

    # --- EXTRAER CUERPO PRINCIPAL ---
    try:
        doc = Document(html)
        summary_html = doc.summary()
        summary_soup = BeautifulSoup(summary_html, "lxml")
        texto_limpio = summary_soup.get_text(" ", strip=True)
    except:
        texto_limpio = texto_bruto  # fallback

    return titulo, fecha, texto_limpio
