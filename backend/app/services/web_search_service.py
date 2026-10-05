"""Search the web for source material used by research sessions."""
import asyncio
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _search_sync(query: str) -> List[Dict[str, str]]:
    from ddgs import DDGS

    results = DDGS().text(query, max_results=5)
    sources = []
    for result in results:
        url = result.get("href") or result.get("url")
        if not url:
            continue
        sources.append(
            {
                "title": result.get("title") or url,
                "url": url,
                "content": result.get("body", ""),
            }
        )
    return sources


async def search_web(query: str) -> List[Dict[str, Any]]:
    """Fetch a small set of web results without blocking the async workflow."""
    try:
        return await asyncio.to_thread(_search_sync, query)
    except Exception:
        logger.exception("Web search failed")
        return []