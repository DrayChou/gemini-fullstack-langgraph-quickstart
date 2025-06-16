from duckduckgo_search import DDGS
from typing import List, Dict, Any, Optional


def web_search(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a web search using DuckDuckGo Search API.
    
    Args:
        query: The search query string
        num_results: Maximum number of results to return (default: 5)
        
    Returns:
        List of search result dictionaries with title, url, and snippet
    """
    try:
        results = []
        with DDGS() as ddgs:
            ddgs_results = ddgs.text(query, max_results=num_results)
            for result in ddgs_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                })
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []


def format_search_results(results: List[Dict[str, Any]]) -> str:
    """
    Formats search results into a readable text format.
    
    Args:
        results: List of search result dictionaries
        
    Returns:
        Formatted string with search results
    """
    if not results:
        return "No results found."
        
    formatted = []
    for i, result in enumerate(results):
        entry = f"[{i+1}] {result.get('title', 'No title')}\n"
        entry += f"URL: {result.get('url', 'No URL')}\n"
        entry += f"Snippet: {result.get('snippet', 'No snippet')}\n"
        formatted.append(entry)
        
    return "\n\n".join(formatted)
