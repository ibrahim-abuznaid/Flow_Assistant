"""
Agent setup with tools and memory.
"""
from typing import Optional, Dict
import logging
from threading import Lock
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.llm_config import get_llm
from src.memory import create_memory
from src.tools import get_all_tools


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
- 450 pieces (integrations)
- 2,890 actions
- 834 triggers
- Full metadata including all input properties and configuration details

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
_AGENT_CACHE: Dict[str, AgentExecutor] = {}
_AGENT_CACHE_LOCK = Lock()
_DEFAULT_SESSION_KEY = "__default__"


def _make_cache_key(session_id: Optional[str]) -> str:
    """Normalize cache key for agent reuse."""
    return session_id or _DEFAULT_SESSION_KEY


def create_direct_agent(session_id: Optional[str] = None) -> AgentExecutor:
    """
    Create a DIRECT agent instance optimized for speed.

    Args:
        session_id: Optional session ID to load conversation history

    Returns:
        AgentExecutor configured for fast execution
    """
    llm = get_llm()
    memory = create_memory(session_id=session_id)
    tools = get_all_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", DIRECT_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=40,
        max_execution_time=120,
        return_intermediate_steps=False
    )

    return agent_executor


def get_agent(session_id: Optional[str] = None) -> AgentExecutor:
    """Get or create an agent executor with session-scoped memory."""
    cache_key = _make_cache_key(session_id)

    with _AGENT_CACHE_LOCK:
        agent_executor = _AGENT_CACHE.get(cache_key)
        if agent_executor is None:
            agent_executor = create_direct_agent(session_id=session_id)
            _AGENT_CACHE[cache_key] = agent_executor

    return agent_executor


def clear_agent_cache(session_id: Optional[str] = None) -> None:
    """Clear cached agents to release memory or refresh state."""
    with _AGENT_CACHE_LOCK:
        if session_id is None:
            for executor in _AGENT_CACHE.values():
                try:
                    executor.memory.clear()
                except Exception:
                    pass
            _AGENT_CACHE.clear()
            return

        cache_key = _make_cache_key(session_id)
        executor = _AGENT_CACHE.pop(cache_key, None)
        if executor is not None:
            try:
                executor.memory.clear()
            except Exception:
                pass
