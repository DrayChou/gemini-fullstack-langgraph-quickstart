"""
OpenAI adapter for compatibility with the LangGraph framework.
Provides a unified interface compatible with ChatGoogleGenerativeAI.
"""

from typing import Any, Dict, List, Optional
import os
import json
from pydantic import Field
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage
)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class CustomOpenAIChat(BaseChatModel):
    """
    Custom wrapper for OpenAI Chat models.
    Provides the same interface as ChatGoogleGenerativeAI for compatibility.
    """
    
    model: str = Field(default="gpt-3.5-turbo")
    temperature: float = Field(default=0.7)
    max_retries: int = Field(default=2)
    api_key: Optional[str] = Field(default=None)
    base_url: Optional[str] = Field(default=None)
    client: Any = Field(default=None, exclude=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Please install with: pip install openai")
        
        # Get API key from parameter or environment
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")
            
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")
        
        # Get base URL from parameter or environment
        if not self.base_url:
            self.base_url = os.getenv("OPENAI_BASE_URL")
            
        # Initialize OpenAI client
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
            
        self.client = OpenAI(**client_kwargs)
        
    @property
    def _llm_type(self) -> str:
        return "custom-openai-chat"

    def _convert_messages(self, messages: List[BaseMessage]) -> List[Dict]:
        """Convert LangChain messages to OpenAI format."""
        openai_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                openai_messages.append({
                    "role": "user",
                    "content": message.content
                })
            elif isinstance(message, AIMessage):
                openai_messages.append({
                    "role": "assistant",
                    "content": message.content
                })
            elif isinstance(message, SystemMessage):
                openai_messages.append({
                    "role": "system",
                    "content": message.content
                })
            elif isinstance(message, ChatMessage):
                openai_messages.append({
                    "role": message.role,
                    "content": message.content
                })
            else:
                # Fallback for unknown message types
                openai_messages.append({
                    "role": "user",
                    "content": str(message.content)
                })
        return openai_messages
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat response using OpenAI API."""
        
        openai_messages = self._convert_messages(messages)
        
        # Prepare API parameters
        params = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": self.temperature,
        }
        
        # Add optional parameters
        if stop:
            params["stop"] = stop
        
        # Override with any additional kwargs
        params.update(kwargs)
        
        try:
            response = self.client.chat.completions.create(**params)
            
            # Extract the response content
            message_content = response.choices[0].message.content or ""
            
            # Create AIMessage
            ai_message = AIMessage(content=message_content)
            
            # Create ChatGeneration
            generation = ChatGeneration(message=ai_message)
            
            return ChatResult(generations=[generation])
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}")
    
    def with_structured_output(self, schema_class):
        """
        Return a wrapper that structures output according to schema.
        Mimics the ChatGoogleGenerativeAI.with_structured_output() interface.
        
        Args:
            schema_class: Pydantic model class for output structure
            
        Returns:
            Wrapper object with invoke method
        """
        
        def invoke(prompt: str):
            """Invoke the model and parse structured output."""
            
            # Get schema information for better prompting
            schema_name = getattr(schema_class, '__name__', 'Output')
            
            # Extract field information from the schema
            schema_fields = []
            if hasattr(schema_class, 'model_fields'):
                for field_name, field_info in schema_class.model_fields.items():
                    field_desc = getattr(field_info, 'description', '')
                    field_type = getattr(field_info.annotation, '__name__', str(field_info.annotation))
                    schema_fields.append(f"- {field_name} ({field_type}): {field_desc}")
            
            schema_description = '\n'.join(schema_fields) if schema_fields else "Follow the provided schema structure"
            
            # Create a more specific prompt for JSON output
            json_prompt = f"""
{prompt}

Please respond with valid JSON that matches the {schema_name} schema exactly.
Required fields:
{schema_description}

Return only the JSON object, without any markdown formatting or additional text.
Ensure all required fields are included.
"""
            
            # Create messages for the API call
            messages = [SystemMessage(content=json_prompt)]
            
            # Generate response
            response = self._generate(messages)
            content = response.generations[0].message.content
            
            return self._parse_structured_response(content, schema_class)
        
        # Create wrapper object
        class StructuredOutputWrapper:
            def __init__(self, invoke_func):
                self.invoke = invoke_func
        
        return StructuredOutputWrapper(invoke)
    
    def _parse_structured_response(self, content: str, schema_class):
        """Parse the model response into structured format."""
        try:
            # Clean the content first
            json_str = self._extract_json_from_response(content)
            
            # Parse JSON and create schema instance
            data = json.loads(json_str)
            return schema_class(**data)
            
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            print(f"Warning: Failed to parse structured output: {e}")
            print(f"Raw response: {content[:200]}...")
            
            # Return default instance on failure
            try:
                return schema_class()
            except Exception:
                # If even default construction fails, return None
                print(f"Error: Could not create default {schema_class.__name__} instance")
                return None
    
    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON string from various response formats."""
        content = content.strip()
        
        # Try to extract JSON from markdown code blocks
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].strip()
        # Try to find JSON object boundaries
        elif content.startswith("{") and content.endswith("}"):
            json_str = content
        elif "{" in content and "}" in content:
            # Extract the first complete JSON object
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
        else:
            # Use content as-is and hope for the best
            json_str = content
            
        return json_str
