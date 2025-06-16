import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    """The configuration for the agent."""    # API Provider Selection
    api_provider: str = Field(
        default="auto",
        metadata={
            "description": "The API provider to use: 'auto', 'openai', or 'gemini'"
        },
    )

    # Search Provider Selection
    search_provider: str = Field(
        default="duckduckgo",
        metadata={
            "description": "The search provider to use: 'duckduckgo' or 'google'"
        },
    )
    
    # Model configurations for different providers
    query_generator_model: str = Field(
        default="",  # Will be set based on provider
        metadata={
            "description": "The name of the language model to use for query generation."
        },
    )
    
    reflection_model: str = Field(
        default="",  # Will be set based on provider
        metadata={
            "description": "The name of the language model to use for reflection."
        },
    )

    answer_model: str = Field(
        default="",  # Will be set based on provider
        metadata={
            "description": "The name of the language model to use for answer."
        },
    )

    # Specific model override (can be set via environment variables)
    openai_model: str = Field(
        default="",
        metadata={
            "description": "Override default OpenAI model (e.g., 'deepseek-v3', 'gpt-4')"
        },
    )
    
    gemini_model: str = Field(
        default="",
        metadata={
            "description": "Override default Gemini model (e.g., 'gemini-2.0-flash-exp')"
        },
    )

    # Proxy configuration
    http_proxy: Optional[str] = Field(
        default=None,
        metadata={
            "description": "HTTP proxy configuration for API calls (format: protocol://host:port)"
        },
    )
    
    https_proxy: Optional[str] = Field(
        default=None,
        metadata={
            "description": "HTTPS proxy configuration for API calls (format: protocol://host:port)"
        },
    )

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "The maximum number of research loops to perform."},
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
    
    def get_effective_api_provider(self) -> str:
        """Get the effective API provider, resolving 'auto' mode."""
        if self.api_provider.lower() != "auto":
            return self.api_provider.lower()
        
        # Auto mode: choose based on available API keys
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        elif os.environ.get("GEMINI_API_KEY"):
            return "gemini"
        else:
            # Default to OpenAI if no keys are available
            return "openai"
    
    def get_default_models(self) -> dict:
        """Get default model configurations based on the effective API provider."""
        effective_provider = self.get_effective_api_provider()
        
        # Check for specific model overrides first
        if effective_provider == "openai":
            default_model = self.openai_model or "deepseek-v3"
            return {
                "query_generator_model": default_model,
                "reflection_model": default_model,
                "answer_model": default_model
            }
        else:  # Gemini
            default_model = self.gemini_model or "gemini-2.0-flash-exp"
            return {
                "query_generator_model": default_model,
                "reflection_model": self.gemini_model or "gemini-2.0-flash-thinking-exp",
                "answer_model": self.gemini_model or "gemini-2.0-flash-thinking-exp"
            }
    
    def get_model(self, model_type: str) -> str:
        """Get the configured model or default for the specified type."""
        current_value = getattr(self, model_type, "")
        if current_value:
            return current_value
        
        defaults = self.get_default_models()
        return defaults.get(model_type, defaults["query_generator_model"])
