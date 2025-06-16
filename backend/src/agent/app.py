# mypy: disable - error - code = "no-untyped-def,misc"
import os
import pathlib
from dotenv import load_dotenv
from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage

# Load environment variables FIRST
load_dotenv()

# Import our graph and configuration
from agent.graph import graph
from agent.configuration import Configuration

# Define the FastAPI app
app = FastAPI(
    title="LangGraph Agent API",
    description="LangGraph Agent with DeepSeek-V3 support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    config: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    messages: List[ChatMessage]
    sources: List[str] = []
    metadata: Dict[str, Any] = {}


# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LangGraph Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "chat": "/chat",
            "invoke": "/invoke",
            "config": "/config"
        }
    }


@app.get("/config")
async def get_config():
    """Get current configuration"""
    config = Configuration.from_runnable_config()
    return {
        "api_provider": config.get_effective_api_provider(),
        "models": {
            "query_generator": config.get_model("query_generator_model"),
            "reflection": config.get_model("reflection_model"),
            "answer": config.get_model("answer_model")
        },
        "search_provider": getattr(config, 'search_provider', 'duckduckgo')
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint - main agent interaction"""
    try:
        # Convert request to LangChain format
        langchain_messages = []
        for msg in request.messages:
            if msg.role == "human" or msg.role == "user":
                langchain_messages.append(HumanMessage(content=msg.content))
        
        # Prepare state for the graph
        state = {
            "messages": langchain_messages,
            "initial_search_query_count": 3,  # Default
            "max_research_loops": 2  # Default
        }
        
        # Create proper configuration including environment variables
        from agent.configuration import Configuration
        base_config = Configuration.from_runnable_config()
        
        # Merge with any user-provided config
        merged_config = {
            "api_provider": base_config.api_provider,
            "search_provider": base_config.search_provider,
            "openai_model": getattr(base_config, 'openai_model', ''),
            "query_generator_model": base_config.get_model('query_generator_model'),
            "reflection_model": base_config.get_model('reflection_model'),
            "answer_model": base_config.get_model('answer_model'),
        }
        
        # Add user config if provided
        if request.config:
            merged_config.update(request.config)
        
        config = {"configurable": merged_config}
        
        # Invoke the graph
        result = graph.invoke(state, config)
        
        # Convert response back to API format
        response_messages = []
        for msg in result.get("messages", []):
            response_messages.append(ChatMessage(
                role="assistant",
                content=msg.content
            ))
        
        # Extract sources
        sources = []
        if "sources_gathered" in result:
            sources = [src.get("url", str(src)) for src in result["sources_gathered"]]
        
        return ChatResponse(
            messages=response_messages,
            sources=sources,
            metadata={
                "query_count": len(result.get("query_list", [])),
                "source_count": len(sources)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/invoke")
async def invoke(request: ChatRequest):
    """Alternative invoke endpoint (alias for chat)"""
    return await chat(request)


# Health check
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-06-15"}


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    return StaticFiles(directory=build_path, html=True)


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
