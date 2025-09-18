"""Simple fetcher for Readwise highlights (or demo data in DRY_RUN).
"""
import os
import json
from typing import List, Dict

DRY_RUN = os.getenv("DRY_RUN")


def fetch_sample_highlights() -> List[Dict]:
    import hashlib

    samples = [
        ("h1", "Scale Converter Notes", "Converter outputs match hand-checked results", ["scale-converter"]),
        ("h2", "DCC Safety Notes", "Hardware control requires explicit opt-in and safety gating.", ["safety"]),
    ]
    out = []
    for hid, source_title, excerpt, tags in samples:
        checksum = hashlib.sha256((excerpt + source_title).encode("utf-8")).hexdigest()
        out.append({
            "id": hid,
            "source": "Readwise",
            "title": source_title,
            "excerpt": excerpt,
            "tags": tags,
            "provenance": {
                "author": "Unknown",
                "source_title": source_title,
                "doc_url": None,
                "exported_at": "2025-09-18T00:00:00Z",
                "checksum": checksum,
            },
        })
    return out


def fetch_from_readwise(token: str) -> List[Dict]:
    import requests
    headers = {"Authorization": f"Token {token}"}
    resp = requests.get("https://readwise.io/api/v2/highlights/", headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # Normalize to a simple list of highlights
    out = []
    for item in data.get("results", []):
        # attach provenance metadata where available
        prov = {
            "author": item.get("author") or None,
            "source_title": item.get("book_title") or None,
            "doc_url": item.get("source_url") or None,
            "exported_at": item.get("updated_at") or item.get("created_at") or None,
            "checksum": None,
        }
        # attempt to compute checksum from excerpt + source_title when available
        try:
            import hashlib

            excerpt = item.get("text", "") or ""
            stitle = prov.get("source_title") or ""
            if excerpt or stitle:
                prov["checksum"] = hashlib.sha256((excerpt + stitle).encode("utf-8")).hexdigest()
        except Exception:
            prov["checksum"] = None
        out.append({
            "id": item.get("id"),
            "source": "Readwise",
            "title": item.get("book_title") or (item.get("source") and item.get("source").get("title")),
            "excerpt": item.get("text"),
            "tags": item.get("tags", []),
            "provenance": prov,
        })
    return out


def fetch_highlights() -> List[Dict]:
    token = os.getenv("READWISE_TOKEN")
    if DRY_RUN or not token:
        return fetch_sample_highlights()
    return fetch_from_readwise(token)


def filter_highlights(highlights: List[Dict], tags_whitelist=None, keywords=None, max_items=None) -> List[Dict]:
    """Filter highlights by tag whitelist and keyword match, and limit results.

    - tags_whitelist: iterable of tags to keep (if None, keep all)
    - keywords: iterable of keywords (case-insensitive) to match in excerpt or title
    - max_items: int or None to limit the number of returned items
    """
    if tags_whitelist:
        tagset = set(t.lower() for t in tags_whitelist)
        highlights = [h for h in highlights if any(t.lower() in tagset for t in (h.get("tags") or []))]

    if keywords:
        kw = [k.lower() for k in keywords]

        def matches(h):
            text = ((h.get("excerpt") or "") + " " + (h.get("title") or "")).lower()
            return any(k in text for k in kw)

        highlights = [h for h in highlights if matches(h)]

    if max_items:
        try:
            n = int(max_items)
            highlights = highlights[:n]
        except Exception:
            pass

    return highlights


if __name__ == "__main__":
    print(json.dumps(fetch_highlights(), indent=2))
