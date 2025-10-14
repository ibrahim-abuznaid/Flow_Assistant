"""
Agent setup with tools and memory.
"""
from typing import Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.llm_config import get_llm
from src.memory import create_memory
from src.tools import ALL_TOOLS
from src.planner import create_guided_input


# System prompt for the agent
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


def create_agent() -> AgentExecutor:
    """
    Create and configure the agent with tools and memory.
    """
    # Initialize LLM
    llm = get_llm()
    
    # Create memory
    memory = create_memory()
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent using modern tool calling (compatible with all models)
    agent = create_tool_calling_agent(
        llm=llm,
        tools=ALL_TOOLS,
        prompt=prompt
    )
    
    # Create agent executor with balanced limits
    agent_executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=25,  # Allows for planning + web search + detailed response
        max_execution_time=120,  # 2 minute timeout (web search + response generation)
        return_intermediate_steps=False
    )
    
    print("✓ Agent created successfully")
    
    return agent_executor


# Global agent instance
_agent = None


def get_agent(session_id: Optional[str] = None) -> AgentExecutor:
    """
    Get or create agent instance with session-specific memory.
    
    Args:
        session_id: Optional session ID to load conversation history
    
    Returns:
        AgentExecutor with loaded session memory
    """
    # Always create a new agent with session-specific memory
    # This ensures conversation history is properly loaded
    from src.memory import create_memory
    
    # Initialize LLM
    llm = get_llm()
    
    # Create memory with session history
    memory = create_memory(session_id=session_id)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create agent using modern tool calling
    agent = create_tool_calling_agent(
        llm=llm,
        tools=ALL_TOOLS,
        prompt=prompt
    )
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=25,
        max_execution_time=120,
        return_intermediate_steps=False
    )
    
    return agent_executor


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
    guided_input = create_guided_input(user_query)
    
    # Step 2: Execute agent with the enhanced input
    result = agent_executor.invoke({"input": guided_input["enhanced_input"]})
    
    # Step 3: Return result with planning metadata
    return {
        "output": result.get("output", ""),
        "plan": guided_input["plan"],
        "original_query": guided_input["original_query"]
    }

