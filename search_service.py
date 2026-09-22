import re
from ddgs import DDGS

def clean_query_for_search(raw_query: str) -> str:
    """
    Strips conversational framing (e.g. 'generate into pdf', 'please write a report')
    to create an effective search query.
    """
    cleaned = raw_query.strip()
    # Remove phrases related to PDF or output format
    cleaned = re.sub(r'(?i)(generate\s+(a\s+|into\s+)?pdf|export\s+(to\s+)?pdf|download\s+pdf|make\s+a\s+pdf)', '', cleaned)
    cleaned = re.sub(r'(?i)(please\s+|can\s+you\s+|write\s+a\s+report\s+on\s+|summarize\s+)', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned if cleaned else raw_query.strip()


def search_live_web(query: str, max_results: int = 3) -> list:
    """
    Searches the live web using DDGS and returns clean results.
    """
    search_term = clean_query_for_search(query)
    if not search_term:
        return []

    results = []
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(search_term, max_results=max_results))
            for item in raw_results:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("body", ""),
                    "link": item.get("href", "")
                })
    except Exception as e:
        print(f"Web search note: {e}")
        return []

    return results


def format_search_context(search_results: list) -> str:
    """
    Formats web search results into a clean prompt context block for the LLM.
    """
    if not search_results:
        return ""

    blocks = ["=== REAL-TIME GROUNDING KNOWLEDGE (CURRENT FACTS) ==="]
    for idx, item in enumerate(search_results, 1):
        blocks.append(
            f"[{idx}] {item['title']}\n"
            f"Key Information: {item['snippet']}\n"
            f"Source URL: {item['link']}\n"
        )
    blocks.append("=====================================================")
    return "\n".join(blocks)
