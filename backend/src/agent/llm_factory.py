import os
from typing import Any
from agent.configuration import Configuration
from agent.openai_adapter import CustomOpenAIChat

# Import Gemini classes conditionally
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    ChatGoogleGenerativeAI = None


class LLMFactory:
    """Factory class for creating LLM instances based on configuration."""
    
    @staticmethod
    def create_llm(
        config: Configuration,
        model_type: str = "query_generator_model",
        temperature: float = 0.7,
        max_retries: int = 2,
        **kwargs
    ) -> Any:
        """
        Create an LLM instance based on the configuration.
        
        Args:
            config: Configuration object containing API provider settings
            model_type: Type of model to create 
            temperature: Sampling temperature for the model
            max_retries: Maximum number of retries for API calls
            **kwargs: Additional parameters to pass to the model
            
        Returns:
            LLM instance ready for use
            
        Raises:
            ValueError: If the specified API provider is not supported
        """
        provider = config.get_effective_api_provider()
        model_name = config.get_model(model_type)
        
        if provider == "openai":
            return LLMFactory._create_openai_llm(
                model_name, temperature, max_retries, **kwargs
            )
        elif provider == "gemini":
            return LLMFactory._create_gemini_llm(
                model_name, temperature, max_retries, **kwargs
            )
        else:
            raise ValueError(f"Unsupported API provider: {provider}")
    
    @staticmethod
    def _create_openai_llm(
        model_name: str,
        temperature: float,
        max_retries: int,
        **kwargs
    ) -> Any:
        """Create an OpenAI LLM instance with proper configuration."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        base_url = os.getenv("OPENAI_BASE_URL")
        
        return CustomOpenAIChat(
            model=model_name,
            temperature=temperature,
            max_retries=max_retries,
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )
    
    @staticmethod
    def _create_gemini_llm(
        model_name: str,
        temperature: float,
        max_retries: int,
        **kwargs
    ) -> Any:
        """Create a Gemini LLM instance."""
        if not GEMINI_AVAILABLE:
            raise ValueError(
                "Gemini models are not available. "
                "Please install langchain-google-genai"
            )
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_retries=max_retries,
            api_key=api_key,
            **kwargs
        )
    
    @staticmethod
    def get_required_api_key(provider: str) -> str:
        """Get the required API key environment variable name."""
        if provider.lower() == "openai":
            return "OPENAI_API_KEY"
        elif provider.lower() == "gemini":
            return "GEMINI_API_KEY"
        elif provider.lower() == "auto":
            # For auto mode, return the first available key
            if os.getenv("OPENAI_API_KEY"):
                return "OPENAI_API_KEY"
            elif os.getenv("GEMINI_API_KEY"):
                return "GEMINI_API_KEY"
            else:
                return "OPENAI_API_KEY"  # Default
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    @staticmethod
    def validate_api_key(provider: str) -> bool:
        """Validate that the required API key is set for the provider."""
        # Handle auto mode
        if provider.lower() == "auto":
            return (os.getenv("OPENAI_API_KEY") is not None or 
                    os.getenv("GEMINI_API_KEY") is not None)
        
        key_name = LLMFactory.get_required_api_key(provider)
        return os.getenv(key_name) is not None
