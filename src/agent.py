"""
Agent setup with tools and memory.
"""
from typing import Optional, Dict, Tuple
import time
import logging
from threading import Lock
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.llm_config import get_llm
from src.memory import create_memory
from src.tools import get_all_tools
from src.planner import create_guided_input


# System prompt for the agent WITH planning layer
SYSTEM_PROMPT = """You are an expert AI assistant for ActivePieces, a workflow automation platform similar to Zapier or Make.com.

Your role is to help users understand and work with ActivePieces by:
1. Answering questions about available integrations (pieces), actions, and triggers
2. Providing COMPLETE guidance including ALL required and optional input properties
3. Explaining features, capabilities, and exact configurations needed
4. Helping troubleshoot and solve automation challenges with detailed step-by-step instructions

You have access to these tools:
- **check_activepieces**: Use this to verify if a specific piece, action, or trigger exists in ActivePieces
- **search_activepieces_docs**: Use this to find detailed information including INPUT PROPERTIES, types, requirements, and options
- **web_search**: Use this for general questions or information not in the ActivePieces knowledge base
- **get_code_generation_guidelines**: Use this BEFORE generating any TypeScript code for flow steps - it provides critical guidelines and best practices

CRITICAL EFFICIENCY RULES:
⚠️ You will receive a PLANNING GUIDE with your query. FOLLOW IT EXACTLY.
⚠️ The plan specifies MAX TOOL CALLS and STOPPING CONDITIONS. DO NOT EXCEED THEM.
⚠️ If a tool fails, use the FALLBACK STRATEGY immediately. Do NOT retry endlessly.
⚠️ "Good enough" information is better than perfect information that takes 20 tool calls.
⚠️ When you hit the stopping condition, RESPOND IMMEDIATELY with what you have.

IMPORTANT GUIDELINES FOR PROVIDING COMPLETE INFORMATION:
- When explaining how to use an action or trigger, ALWAYS include:
  * The action/trigger name and description
  * ALL INPUT PROPERTIES (both required and optional)
  * Property types (text, number, dropdown, etc.)
  * Which properties are required vs optional
  * Available options for dropdown fields
  * Default values if any
  * Property descriptions to explain what each input does

- Use search_activepieces_docs to get complete property information before responding
- When creating a plan or instructions, list ALL inputs the user needs to configure
- Be specific about data types and validation requirements
- Provide examples of valid input values when helpful
- If the knowledge base doesn't have complete info, say so explicitly and MOVE ON

CODE GENERATION FORMATTING:
- When generating TypeScript code, ALWAYS wrap it in markdown code blocks:
  ```typescript
  export const code = async (inputs: {{...}}) => {{
    // code here
  }}
  ```
- When returning JSON (like code responses), wrap in json code blocks:
  ```json
  {{
    "code": "...",
    "inputs": [...],
    "title": "..."
  }}
  ```
- Use appropriate language tags: typescript, json, javascript, python, etc.
- This ensures code displays properly with syntax highlighting in the UI

Remember: You have access to a comprehensive database with:
- 433 pieces (integrations)
- 2,681 actions
- 694 triggers
- 10,118 input properties with full details

EFFICIENCY OVER PERFECTION: Provide the best answer with the information you gather within the allowed tool calls. Don't chase completeness if it means exceeding limits."""


# System prompt for DIRECT agent (without planning layer) - Optimized for speed
DIRECT_SYSTEM_PROMPT = """You are an expert AI assistant for ActivePieces, a workflow automation platform similar to Zapier or Make.com.

Your role is to help users understand and work with ActivePieces by:
1. Answering questions about available integrations (pieces), actions, and triggers
2. Providing COMPLETE guidance including ALL required and optional input properties
3. Explaining features, capabilities, and exact configurations needed
4. Helping troubleshoot and solve automation challenges with detailed step-by-step instructions

You have access to these tools:
- **check_activepieces**: Use this to verify if a specific piece, action, or trigger exists in ActivePieces
- **search_activepieces_docs**: Use this to find detailed information including INPUT PROPERTIES, types, requirements, and options
- **web_search**: Use this for general questions or information not in the ActivePieces knowledge base
- **get_code_generation_guidelines**: Use this BEFORE generating any TypeScript code for flow steps - it provides critical guidelines and best practices

EFFICIENCY GUIDELINES:
- Be concise and direct in your responses
- Use tools strategically - prefer 1-2 focused searches over many
- If information is not found quickly, acknowledge limitations and move forward
- Prioritize answering the user's question over gathering perfect details

IMPORTANT GUIDELINES FOR PROVIDING COMPLETE INFORMATION:
- When explaining how to use an action or trigger, ALWAYS include:
  * The action/trigger name and description
  * ALL INPUT PROPERTIES (both required and optional)
  * Property types (text, number, dropdown, etc.)
  * Which properties are required vs optional
  * Available options for dropdown fields
  * Default values if any
  * Property descriptions to explain what each input does

- Use search_activepieces_docs to get complete property information before responding
- When creating a plan or instructions, list ALL inputs the user needs to configure
- Be specific about data types and validation requirements
- Provide examples of valid input values when helpful
- If the knowledge base doesn't have complete info, say so explicitly and provide what you have

CODE GENERATION FORMATTING:
- When generating TypeScript code, ALWAYS wrap it in markdown code blocks:
  ```typescript
  export const code = async (inputs: {{...}}) => {{
    // code here
  }}
  ```
- When returning JSON (like code responses), wrap in json code blocks:
  ```json
  {{
    "code": "...",
    "inputs": [...],
    "title": "..."
  }}
  ```
- Use appropriate language tags: typescript, json, javascript, python, etc.
- This ensures code displays properly with syntax highlighting in the UI

Remember: You have access to a comprehensive database with:
- 433 pieces (integrations)
- 2,681 actions
- 694 triggers
- 10,118 input properties with full details

Be efficient, direct, and helpful. Quality answers within 1-3 tool calls are better than perfect answers that take 10+ calls."""


# Module-level logger for consistent timing output across environments
logger = logging.getLogger("flow_assistant.agent")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False


# Simple cache for reusing agent executors (reduces per-request setup overhead)
_AGENT_CACHE: Dict[Tuple[bool, str], AgentExecutor] = {}
_AGENT_CACHE_LOCK = Lock()
_DEFAULT_SESSION_KEY = "__default__"


def _make_cache_key(use_planning: bool, session_id: Optional[str]) -> Tuple[bool, str]:
    """Normalize cache key for agent reuse."""
    return (use_planning, session_id or _DEFAULT_SESSION_KEY)


def _create_planning_agent(session_id: Optional[str] = None, max_execution_time: int = 120) -> AgentExecutor:
    """Create an agent executor that expects a planning guide."""
    llm = get_llm()
    memory = create_memory(session_id=session_id)
    tools = get_all_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=25,
        max_execution_time=max_execution_time,
        return_intermediate_steps=False
    )


def create_agent() -> AgentExecutor:
    """
    Create and configure the agent with tools and memory.
    """
    agent_executor = _create_planning_agent(max_execution_time=300)
    print("✓ Agent created successfully")
    
    return agent_executor


def create_direct_agent(session_id: Optional[str] = None) -> AgentExecutor:
    """
    Create a DIRECT agent instance WITHOUT planning layer - optimized for speed.
    
    Args:
        session_id: Optional session ID to load conversation history
    
    Returns:
        AgentExecutor configured for fast execution
    """
    # Initialize LLM
    llm = get_llm()
    
    # Create memory with session history
    memory = create_memory(session_id=session_id)
    
    # Get tools with lazy loading
    tools = get_all_tools()
    
    # Create prompt template with DIRECT prompt (no planning instructions)
    prompt = ChatPromptTemplate.from_messages([
        ("system", DIRECT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent using modern tool calling
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # Create agent executor with optimized limits for speed
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=40,  # Reduced from 25 for faster execution
        max_execution_time=120,  # Reduced from 300s for faster timeout
        return_intermediate_steps=False
    )
    
    return agent_executor


def get_agent(session_id: Optional[str] = None, use_planning: bool = True) -> AgentExecutor:
    """
    Get or create agent instance with session-specific memory.
    
    Args:
        session_id: Optional session ID to load conversation history
        use_planning: If True, uses agent with planning prompt. If False, uses direct agent.
    
    Returns:
        AgentExecutor with loaded session memory
    """
    cache_key = _make_cache_key(use_planning, session_id)

    with _AGENT_CACHE_LOCK:
        agent_executor = _AGENT_CACHE.get(cache_key)
        if agent_executor is None:
            agent_executor = _create_planning_agent(session_id=session_id) if use_planning else create_direct_agent(session_id=session_id)
            _AGENT_CACHE[cache_key] = agent_executor

    return agent_executor


def clear_agent_cache(session_id: Optional[str] = None, use_planning: Optional[bool] = None) -> None:
    """Clear cached agents to release memory or refresh state."""
    with _AGENT_CACHE_LOCK:
        if session_id is None and use_planning is None:
            for executor in _AGENT_CACHE.values():
                try:
                    executor.memory.clear()
                except Exception:
                    pass
            _AGENT_CACHE.clear()
            return

        normalized_session = session_id or _DEFAULT_SESSION_KEY
        keys_to_remove = []

        for key in list(_AGENT_CACHE.keys()):
            matches_session = session_id is None or key[1] == normalized_session
            matches_mode = use_planning is None or key[0] == use_planning
            if matches_session and matches_mode:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            executor = _AGENT_CACHE.pop(key, None)
            if executor is not None:
                try:
                    executor.memory.clear()
                except Exception:
                    pass


def run_agent_with_planning(user_query: str, agent_executor: AgentExecutor, session_id: Optional[str] = None) -> dict:
    """
    Run the agent with planning layer.
    
    Args:
        user_query: The user's input query
        agent_executor: The agent executor instance
        
    Returns:
        Dictionary with agent output and planning metadata
    """
    # Step 1: Planning layer - analyze query and create execution plan
    total_start = time.perf_counter()

    planning_start = time.perf_counter()
    guided_input = create_guided_input(user_query)
    planning_duration = time.perf_counter() - planning_start
    logger.info("Planning step completed in %.2fs", planning_duration)
    
    # Step 2: Execute agent with the enhanced input
    execution_start = time.perf_counter()
    result = agent_executor.invoke({"input": guided_input["enhanced_input"]})
    execution_duration = time.perf_counter() - execution_start
    logger.info("Execution step completed in %.2fs", execution_duration)

    total_duration = time.perf_counter() - total_start
    logger.info("Total run completed in %.2fs", total_duration)
    
    # Step 3: Return result with planning metadata
    return {
        "output": result.get("output", ""),
        "plan": guided_input["plan"],
        "original_query": guided_input["original_query"]
    }

