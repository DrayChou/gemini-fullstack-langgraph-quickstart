from typing import Dict, List, Any
import json

def get_citations_openai(response, resolved_urls_map):
    """
    Extracts citation information from an OpenAI response with citation metadata.
    
    This is an adapted version of the Google Gemini citation processing function,
    modified to work with OpenAI responses with optional tool calls containing citation data.
    
    Args:
        response: The OpenAI response object
        resolved_urls_map: Dictionary mapping original URLs to short URL references
        
    Returns:
        list: A list of citation dictionaries similar to the Gemini version
    """
    citations = []
    
    try:
        # For OpenAI, we'll extract citations from tool_calls if available
        # This assumes that search results have been organized in a similar structure
        if not hasattr(response, "tool_calls") or not response.tool_calls:
            return citations
            
        for tool_call in response.tool_calls:
            if tool_call.type != "function" or tool_call.function.name != "cite_sources":
                continue
                
            try:
                args = json.loads(tool_call.function.arguments)
                if "citations" not in args:
                    continue
                    
                for citation_data in args["citations"]:
                    citation = {}
                    if "start_index" not in citation_data or "end_index" not in citation_data:
                        continue
                        
                    citation["start_index"] = citation_data["start_index"]
                    citation["end_index"] = citation_data["end_index"]
                    citation["segments"] = []
                    
                    if "sources" in citation_data:
                        for source in citation_data["sources"]:
                            url = source.get("url", "")
                            resolved_url = resolved_urls_map.get(url, f"https://source.ai/id/{len(resolved_urls_map)}")
                            if url not in resolved_urls_map:
                                resolved_urls_map[url] = resolved_url
                                
                            citation["segments"].append({
                                "label": source.get("title", "Source"),
                                "short_url": resolved_url,
                                "value": url
                            })
                    
                    if citation["segments"]:
                        citations.append(citation)
            except (json.JSONDecodeError, AttributeError, KeyError) as e:
                print(f"Error processing citation tool call: {e}")
                continue
    except Exception as e:
        print(f"Error in citation extraction: {e}")
        
    return citations


def resolve_urls_openai(search_results: List[Dict[str, Any]], id: int) -> Dict[str, str]:
    """
    Create a map of search result URLs to shorter reference URLs.
    
    Args:
        search_results: List of search result items with URLs
        id: A unique identifier for this search batch
        
    Returns:
        Dictionary mapping original URLs to shortened reference URLs
    """
    resolved_map = {}
    prefix = f"https://search.ai/id/"
    
    for idx, result in enumerate(search_results):
        if "url" in result and result["url"] not in resolved_map:
            resolved_map[result["url"]] = f"{prefix}{id}-{idx}"
    
    return resolved_map
