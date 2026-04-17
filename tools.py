import requests
from bs4 import BeautifulSoup

DUCKDUCKGO_URL = "https://html.duckduckgo.com/html/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ContentPipelineAgent/1.0)"}


def web_search(query: str, max_results: int = 5) -> list[str]:
    """Search DuckDuckGo's HTML endpoint and return a list of result strings."""
    response = requests.post(DUCKDUCKGO_URL, data={"q": query}, headers=HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    results = []
    for result in soup.select(".result")[:max_results]:
        title_el = result.select_one(".result__a")
        snippet_el = result.select_one(".result__snippet")
        if not title_el:
            continue
        title = title_el.get_text(strip=True)
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""
        url = title_el.get("href", "")
        results.append(f"{title} — {snippet} ({url})")

    return results
