from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import re

import requests
from duckduckgo_search import DDGS


@dataclass
class Evidence:
    source: str          # "wikipedia" or "duckduckgo"
    title: str
    url: str
    snippet: str


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


WIKIPEDIA_HEADERS = {
    "User-Agent": "TruthGPT/0.1 (educational project; contact: youremail@example.com)",
}


def wikipedia_search(query: str, limit: int = 3) -> List[Evidence]:
    """
    Wikipedia search API: returns titles + small snippet.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit,
        "utf8": 1,
    }

    r = requests.get(url, params=params, headers=WIKIPEDIA_HEADERS, timeout=20)
    r.raise_for_status()
    data = r.json()

    results: List[Evidence] = []
    for item in data.get("query", {}).get("search", []):
        title = item.get("title", "")
        page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

        snippet_html = item.get("snippet", "") or ""
        snippet_text = re.sub(r"<.*?>", "", snippet_html)
        snippet = _clean(snippet_text)

        results.append(Evidence(source="wikipedia", title=title, url=page_url, snippet=snippet))

    return results


def wikipedia_extract(title: str, chars: int = 12000) -> Optional[Evidence]:
    """
    Fetch a longer plain-text extract for a Wikipedia page title.
    """
    if not title:
        return None

    api = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "exchars": chars,
        "titles": title,
        "format": "json",
        "utf8": 1,
    }

    r = requests.get(api, params=params, headers=WIKIPEDIA_HEADERS, timeout=25)
    if r.status_code != 200:
        return None

    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return None

    page = next(iter(pages.values()))
    extract = _clean(page.get("extract") or "")
    if not extract:
        return None

    page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    return Evidence(source="wikipedia", title=title, url=page_url, snippet=extract)


def duckduckgo_search(query: str, limit: int = 3) -> List[Evidence]:
    results: List[Evidence] = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=limit):
            results.append(
                Evidence(
                    source="duckduckgo",
                    title=item.get("title") or "",
                    url=item.get("href") or "",
                    snippet=_clean(item.get("body") or ""),
                )
            )
    return results


def gather_evidence(query: str, per_source: int = 3) -> List[Evidence]:
    """
    Gather evidence from sources.
    Wikipedia: search -> fetch longer extracts for top titles.
    """
    ev: List[Evidence] = []

    # Wikipedia (extract evidence)
    try:
        wiki_hits = wikipedia_search(query, limit=per_source)
        for hit in wiki_hits:
            ext = wikipedia_extract(hit.title, chars=12000)
            if ext:
                ev.append(ext)
            else:
                ev.append(hit)
    except Exception:
        pass

    # DuckDuckGo (optional)
    try:
        ev.extend(duckduckgo_search(query, limit=per_source))
    except Exception:
        pass

    return ev