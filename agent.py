"""
Agent setup with tools and memory.
"""
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from llm_config import get_llm
from memory import create_memory
from tools import ALL_TOOLS


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

IMPORTANT GUIDELINES FOR PROVIDING COMPLETE INFORMATION:
- When explaining how to use an action or trigger, ALWAYS include:
  * The action/trigger name and description
  * ALL INPUT PROPERTIES (both required and optional)
  * Property types (text, number, dropdown, etc.)
  * Which properties are required vs optional
  * Available options for dropdown fields
  * Default values if any
  * Property descriptions to explain what each input does

- Always use search_activepieces_docs to get complete property information before responding
- When creating a plan or instructions, list ALL inputs the user needs to configure
- Be specific about data types and validation requirements
- Provide examples of valid input values when helpful
- If the knowledge base doesn't have complete info, say so explicitly

Remember: You have access to a comprehensive database with:
- 433 pieces (integrations)
- 2,681 actions
- 694 triggers
- 10,118 input properties with full details

Your responses should give users EVERYTHING they need to successfully configure their workflows without guessing."""


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
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=20,  # Increased to allow comprehensive responses with full property details
        return_intermediate_steps=False
    )
    
    print("✓ Agent created successfully")
    
    return agent_executor


# Global agent instance
_agent = None


def get_agent() -> AgentExecutor:
    """Get or create the global agent instance."""
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent

