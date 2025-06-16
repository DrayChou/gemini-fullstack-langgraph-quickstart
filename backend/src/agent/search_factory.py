import os
from typing import List, Dict, Any, Optional
from agent.configuration import Configuration
from agent.search_adapter import web_search, format_search_results

# Import Google search client conditionally
try:
    from google.genai import Client as GenAIClient
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False
    GenAIClient = None


class SearchFactory:
    """Factory class for creating search instances based on configuration."""
    
    @staticmethod
    def create_search_client(config: Configuration) -> Any:
        """Create a search client based on the configuration."""
        provider = config.api_provider.lower()
        
        if provider == "gemini" and GOOGLE_SEARCH_AVAILABLE:
            # Use Google GenAI client for Gemini when available
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                return GenAIClient(api_key=api_key)
        
        # Fallback to DuckDuckGo search for all other cases
        return None  # DuckDuckGo doesn't need a client
    
    @staticmethod
    def perform_search(
        query: str,
        config: Configuration,
        search_client: Optional[Any] = None,
        num_results: int = 5
    ) -> tuple[List[Dict[str, Any]], str]:
        """
        Perform web search using the appropriate method.
        
        Returns:
            Tuple of (search_results, formatted_text)
        """
        provider = config.api_provider.lower()
        
        if provider == "gemini" and search_client and GOOGLE_SEARCH_AVAILABLE:
            # Use Google's native search when available
            return SearchFactory._google_native_search(
                query, search_client, config, num_results
            )
        else:
            # Use DuckDuckGo search as fallback
            return SearchFactory._duckduckgo_search(query, num_results)
    
    @staticmethod
    def _google_native_search(
        query: str,
        client: Any,
        config: Configuration,
        num_results: int
    ) -> tuple[List[Dict[str, Any]], str]:
        """Perform search using Google's native search API."""
        try:
            response = client.models.generate_content(
                model=config.get_model("query_generator_model"),
                contents=f"Search for: {query}",
                config={
                    "tools": [{"google_search": {}}],
                    "temperature": 0,
                },
            )
            
            # Extract search results from Google response
            search_results = []
            if (hasattr(response, 'candidates') and
                    response.candidates and
                    hasattr(response.candidates[0], 'grounding_metadata')):
                
                grounding_data = response.candidates[0].grounding_metadata
                if hasattr(grounding_data, 'grounding_chunks'):
                    for chunk in grounding_data.grounding_chunks[:num_results]:
                        if hasattr(chunk, 'web'):
                            search_results.append({
                                "title": chunk.web.title,
                                "url": chunk.web.uri,
                                "snippet": getattr(chunk.web, 'snippet', '')
                            })
            
            formatted_text = response.text if hasattr(response, 'text') else ""
            return search_results, formatted_text
            
        except Exception as e:
            print(f"Google search failed, falling back to DuckDuckGo: {e}")
            return SearchFactory._duckduckgo_search(query, num_results)
    
    @staticmethod
    def _duckduckgo_search(
        query: str,
        num_results: int
    ) -> tuple[List[Dict[str, Any]], str]:
        """Perform search using DuckDuckGo."""
        search_results = web_search(query, num_results)
        formatted_text = format_search_results(search_results)
        return search_results, formatted_text
