from crewai.tools import tool
from duckduckgo_search import DDGS
import os, datetime

@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for up-to-date information on a topic. Input should be a search query string."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=6))
        if not results:
            return "No results found."
        lines = []
        for r in results:
            lines.append(f"Title: {r.get('title','')}\nSnippet: {r.get('body','')}\nSource: {r.get('href','')}")
        return "\n\n---\n\n".join(lines)
    except Exception as e:
        return f"Search error: {e}"

@tool("Save Article")
def save_article(content: str) -> str:
    """Save the final article to the output folder. Input should be the full article text."""
    try:
        os.makedirs("output", exist_ok=True)
        ts       = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"output/article_{ts}.md"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Article saved to {filepath}"
    except Exception as e:
        return f"Save error: {e}"
