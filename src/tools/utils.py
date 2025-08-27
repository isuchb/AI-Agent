import requests
from bs4 import BeautifulSoup

def fetch_and_clean(url: str, max_chars: int = 15000) -> str:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    for t in soup(["script", "style", "noscript"]): t.extract()
    text = " ".join(soup.get_text(" ", strip=True).split())
    return text[:max_chars]
