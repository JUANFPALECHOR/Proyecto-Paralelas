from bs4 import BeautifulSoup
from readability import Document

def clean_html(html_bytes):
    html = html_bytes.decode("utf-8", errors="ignore")

    
    doc = Document(html)
    summary_html = doc.summary()

    soup = BeautifulSoup(summary_html, "lxml")
    text = soup.get_text(separator=" ", strip=True)

    return text
