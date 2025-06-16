from agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig

from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from agent.utils import (
    get_research_topic,
)
from agent.llm_factory import LLMFactory
from agent.search_factory import SearchFactory

load_dotenv()


# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """Generate search queries based on the User's question.

    Uses the configured LLM provider to create optimized search queries.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable

    Returns:
        Dictionary with state update, including generated queries
    """
    configurable = Configuration.from_runnable_config(config)

    # Validate API key for the selected provider
    if not LLMFactory.validate_api_key(configurable.api_provider):
        required_key = LLMFactory.get_required_api_key(configurable.api_provider)
        raise ValueError(f"{required_key} is not set")

    # Check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    # Create LLM using factory
    llm = LLMFactory.create_llm(
        config=configurable,
        model_type="query_generator_model",
        temperature=1.0,
        max_retries=2,
    )
    structured_llm = llm.with_structured_output(SearchQueryList)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    
    # Generate the search queries
    result = structured_llm.invoke(formatted_prompt)
    return {"query_list": result.query}


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """Perform web research using the configured search method.

    Executes a web search and generates a summary of the results.

    Args:
        state: Current graph state containing the search query
        config: Configuration for the runnable

    Returns:
        Dictionary with state update, including sources and research results
    """
    configurable = Configuration.from_runnable_config(config)
    
    # Create search client and perform search
    search_client = SearchFactory.create_search_client(configurable)
    search_results, initial_summary = SearchFactory.perform_search(
        state["search_query"],
        configurable,
        search_client,
        num_results=5
    )
    
    # If we have a summary from Google search, use it, otherwise generate one
    if initial_summary:
        research_summary = initial_summary
    else:
        # Create a summary using the configured LLM
        formatted_prompt = web_searcher_instructions.format(
            current_date=get_current_date(),
            research_topic=state["search_query"],
        ) + f"\n\nSearch Results:\n{SearchFactory._duckduckgo_search(state['search_query'], 5)[1]}"
        
        llm = LLMFactory.create_llm(
            config=configurable,
            model_type="query_generator_model",
            temperature=0.0,
            max_retries=2,
        )
        
        # Generate response based on search results
        if hasattr(llm, '_generate'):
            response = llm._generate([AIMessage(content=formatted_prompt)])
            research_summary = response.generations[0].message.content
        else:
            # For Gemini models using invoke method
            research_summary = llm.invoke(formatted_prompt).content
    
    # Create simplified source references
    sources_gathered = []
    for i, result in enumerate(search_results):
        short_url = f"https://ref.ai/id/{state['id']}-{i}"
        sources_gathered.append({
            "label": result.get("title", f"Source {i+1}"),
            "short_url": short_url,
            "value": result.get("url", "")
        })
    
    return {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": [research_summary],
    }


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """Identify knowledge gaps and generate follow-up queries.

    Analyzes current research to identify areas for further research and
    generates potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing research results
        config: Configuration for the runnable

    Returns:
        Dictionary with state update, including follow-up queries
    """
    configurable = Configuration.from_runnable_config(config)
    # Increment the research loop count
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )
    
    # Create reasoning model using factory
    llm = LLMFactory.create_llm(
        config=configurable,
        model_type="reflection_model",
        temperature=1.0,
        max_retries=2,
    )
    result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """Finalize the research answer.

    Prepares the final output by formatting sources and combining them
    with the research results to create a well-structured response.

    Args:
        state: Current graph state containing research results and sources

    Returns:
        Dictionary with state update, including final answer and sources
    """
    configurable = Configuration.from_runnable_config(config)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    # Create answer model using factory
    llm = LLMFactory.create_llm(
        config=configurable,
        model_type="answer_model",
        temperature=0,
        max_retries=2,
    )
    
    # Generate the final answer
    if hasattr(llm, '_generate'):
        # For custom OpenAI adapter
        response = llm._generate([AIMessage(content=formatted_prompt)])
        result_content = response.generations[0].message.content
    else:
        # For Gemini models
        response = llm.invoke(formatted_prompt)
        result_content = response.content

    # Replace the short urls with the original urls and track used sources
    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in result_content:
            result_content = result_content.replace(
                source["short_url"], source["value"]
            )
            unique_sources.append(source)

    return {
        "messages": [AIMessage(content=result_content)],
        "sources_gathered": unique_sources,
    }

    return {
        "messages": [AIMessage(content=result_content)],
        "sources_gathered": unique_sources,
    }


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")
