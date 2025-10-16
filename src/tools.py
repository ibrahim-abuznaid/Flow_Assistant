"""
Tools for the AI assistant agent.
"""
import os
import requests
from typing import Optional, List, Dict, Any
from src.db_config import get_db_cursor
from src.activepieces_db import ActivepiecesDB


# Global variables for caching
_vector_store = None
_embeddings = None


def get_vector_store():
    """Load or return cached vector store."""
    global _vector_store, _embeddings
    if _vector_store is None:
        import pickle
        import faiss
        import numpy as np
        from openai import OpenAI
        
        # Import langchain components (avoiding langchain-openai)
        try:
            from langchain_community.docstore.in_memory import InMemoryDocstore
            from langchain.schema import Document
            from langchain_community.vectorstores import FAISS
            from langchain.embeddings.base import Embeddings
        except Exception as e:
            raise ImportError(f"Failed to import langchain components: {e}. Please ensure langchain packages are properly installed.")
        
        # Load the FAISS index
        index = faiss.read_index("data/ap_faiss_index/index.faiss")
        
        # Load the docstore and index mapping
        with open("data/ap_faiss_index/index.pkl", "rb") as f:
            docstore_dict, index_to_docstore_id = pickle.load(f)
        
        # Convert dict docstore to InMemoryDocstore with Document objects
        documents = {}
        for doc_id, doc_data in docstore_dict.items():
            documents[doc_id] = Document(
                page_content=doc_data['page_content'],
                metadata=doc_data['metadata']
            )
        
        docstore = InMemoryDocstore(documents)
        
        # Create custom embeddings class using OpenAI directly (avoiding langchain-openai compatibility issues)
        class CustomOpenAIEmbeddings(Embeddings):
            def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
                # Create OpenAI client without proxies parameter to avoid compatibility issues
                self.client = OpenAI(
                    api_key=api_key,
                    http_client=None  # Let OpenAI use default http client
                )
                self.model = model
            
            def embed_documents(self, texts: list[str]) -> list[list[float]]:
                """Embed a list of documents."""
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.model
                )
                return [item.embedding for item in response.data]
            
            def embed_query(self, text: str) -> list[float]:
                """Embed a single query."""
                response = self.client.embeddings.create(
                    input=[text],
                    model=self.model
                )
                return response.data[0].embedding
        
        # Initialize custom embeddings
        api_key = os.getenv("OPENAI_API_KEY")
        _embeddings = CustomOpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-ada-002"
        )
        
        # Create FAISS vector store from components
        _vector_store = FAISS(
            embedding_function=_embeddings,
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id
        )
    return _vector_store


def find_piece_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Find a piece by name (case-insensitive, prioritizing exact matches) from SQLite database."""
    name_lower = name.lower().strip()
    
    try:
        with ActivepiecesDB() as db:
            # Try exact match first
            piece = db.get_piece_details(name_lower)
            
            # If no exact match, try searching
            if not piece:
                results = db.search_pieces(name_lower, limit=1)
                if results:
                    piece_name = results[0]['name']
                    piece = db.get_piece_details(piece_name)
            
            if not piece:
                return None
            
            # Format result similar to expected structure
            return {
                'displayName': piece['display_name'],
                'name': piece['name'],
                'slug': piece['name'],
                'description': piece.get('description') or '',
                'categories': piece.get('categories') or [],
                'actions': [{'displayName': a['display_name'], 'description': a.get('description') or ''} for a in piece.get('actions', [])],
                'triggers': [{'displayName': t['display_name'], 'description': t.get('description') or ''} for t in piece.get('triggers', [])]
            }
            
    except Exception as e:
        print(f"Error finding piece: {e}")
        return None


def find_action_by_name(action_name: str) -> List[Dict[str, str]]:
    """Find which pieces have an action with the given name from SQLite database."""
    action_lower = action_name.lower()
    
    try:
        with ActivepiecesDB() as db:
            results = db.search_actions(action_lower, limit=50)
            
            # Convert to expected format
            return [
                {
                    'piece': row['piece_display_name'],
                    'action': row['action_display_name'],
                    'description': row.get('description') or ''
                }
                for row in results
            ]
            
    except Exception as e:
        print(f"Error finding actions: {e}")
        return []


def find_trigger_by_name(trigger_name: str) -> List[Dict[str, str]]:
    """Find which pieces have a trigger with the given name from SQLite database."""
    trigger_lower = trigger_name.lower()
    
    try:
        with ActivepiecesDB() as db:
            # Use the search functionality - search in actions will also find triggers
            # Since the helper doesn't have a search_triggers method, we'll query directly
            with get_db_cursor() as cur:
                cur.execute("""
                    SELECT 
                        p.display_name as piece,
                        t.display_name as trigger,
                        t.description
                    FROM triggers t
                    JOIN pieces p ON t.piece_id = p.id
                    WHERE 
                        LOWER(t.display_name) LIKE ? 
                        OR LOWER(t.name) LIKE ?
                    ORDER BY p.display_name, t.display_name
                    LIMIT 50
                """, (f'%{trigger_lower}%', f'%{trigger_lower}%'))
                
                results = cur.fetchall()
                
                # Convert to list of dicts
                return [
                    {
                        'piece': row['piece'],
                        'trigger': row['trigger'],
                        'description': row['description'] or ''
                    }
                    for row in results
                ]
            
    except Exception as e:
        print(f"Error finding triggers: {e}")
        return []


def check_activepieces(query: str) -> str:
    """
    Check if an integration, action, or trigger exists in ActivePieces.
    Use this tool to verify if a specific piece, action, or trigger is available.
    
    Args:
        query: The name of the piece, action, or trigger to check
        
    Returns:
        Information about whether it exists and its details
    """
    query = query.strip()
    
    # Try to find as a piece (with error handling)
    try:
        piece = find_piece_by_name(query)
    except Exception as e:
        return f"⚠️ Database connection failed. Unable to verify if '{query}' exists in ActivePieces.\n\n" \
               f"Fallback: Please check the ActivePieces web UI directly at your ActivePieces instance.\n" \
               f"Most common integrations include: Gmail, Slack, Google Drive, Google Sheets, Discord, Telegram, HTTP Request, Webhooks, Email, and 400+ more."
    
    if piece:
        piece_name = piece.get("displayName", "")
        description = piece.get("description", "")
        categories = ", ".join(piece.get("categories", []))
        
        actions = [a.get("displayName", "") for a in piece.get("actions", [])]
        triggers = [t.get("displayName", "") for t in piece.get("triggers", [])]
        
        result = f"✓ Yes, ActivePieces has '{piece_name}' integration.\n"
        result += f"Description: {description}\n"
        result += f"Categories: {categories}\n"
        
        if actions:
            result += f"Actions ({len(actions)}): {', '.join(actions[:5])}"
            if len(actions) > 5:
                result += f" and {len(actions) - 5} more"
            result += "\n"
        
        if triggers:
            result += f"Triggers ({len(triggers)}): {', '.join(triggers[:5])}"
            if len(triggers) > 5:
                result += f" and {len(triggers) - 5} more"
        
        return result
    
    # Try to find as an action
    actions = find_action_by_name(query)
    if actions:
        result = f"✓ Found {len(actions)} action(s) matching '{query}':\n\n"
        for i, action in enumerate(actions[:3], 1):
            result += f"{i}. {action['action']} (in {action['piece']})\n"
            result += f"   Description: {action['description']}\n"
        
        if len(actions) > 3:
            result += f"\n... and {len(actions) - 3} more actions"
        
        return result
    
    # Try to find as a trigger
    triggers = find_trigger_by_name(query)
    if triggers:
        result = f"✓ Found {len(triggers)} trigger(s) matching '{query}':\n\n"
        for i, trigger in enumerate(triggers[:3], 1):
            result += f"{i}. {trigger['trigger']} (in {trigger['piece']})\n"
            result += f"   Description: {trigger['description']}\n"
        
        if len(triggers) > 3:
            result += f"\n... and {len(triggers) - 3} more triggers"
        
        return result
    
    return f"✗ NO - ActivePieces does NOT have a '{query}' integration/piece.\n\n" \
           f"It's not available as a built-in piece, action, or trigger in ActivePieces. " \
           f"You may need to use HTTP requests or webhooks to integrate with {query}."


def search_activepieces_docs(query: str) -> str:
    """
    Search the ActivePieces knowledge base for relevant information.
    Use this tool to find information about how to do something, what actions to use,
    or to get contextual information about ActivePieces features.
    
    Args:
        query: The question or topic to search for
        
    Returns:
        Relevant information from the knowledge base
    """
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search(query, k=6)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        # Format results
        snippets = []
        for i, doc in enumerate(results, 1):
            snippets.append(f"Result {i}:\n{doc.page_content}\n")
        
        return "\n".join(snippets)
    
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"


def web_search(query: str) -> str:
    """
    Search the web for current information using OpenAI or Perplexity API.
    Use this tool when the information is not available in the ActivePieces knowledge base
    or when you need real-time/current information.
    
    Args:
        query: The search query
        
    Returns:
        Information from the web
    """
    search_provider = os.getenv("SEARCH_PROVIDER", "openai").lower()
    
    if search_provider == "openai":
        return _search_with_openai(query)
    elif search_provider == "perplexity":
        return _search_with_perplexity(query)
    else:
        return f"Unknown search provider: {search_provider}. Please set SEARCH_PROVIDER to 'openai' or 'perplexity'."


def get_code_generation_guidelines(context: str = "general") -> str:
    """
    Get comprehensive guidelines for generating TypeScript code for ActivePieces automation flows.
    Use this tool whenever you need to generate or help users write code pieces.
    
    Args:
        context: The type of code to generate (e.g., 'api_call', 'data_transform', 'general')
        
    Returns:
        Detailed guidelines and best practices for code generation
    """
    
    base_guidelines = """
=== ACTIVEPIECES CODE GENERATION GUIDELINES ===

🎯 CORE CONCEPT:
You are generating code for a SINGLE STEP in an automation flow, NOT a backend service.
This code will run as ONE step in a larger flow where:
- Previous steps provide inputs
- Next steps will use the outputs
- Authentication is handled by flow connections
- Each step should do ONE thing well

📋 CRITICAL REQUIREMENTS:

1. FUNCTION STRUCTURE:
   ✓ MUST start with 'export const code ='
   ✓ MUST be an async function
   ✓ MUST have proper input parameters with TypeScript types
   ✓ MUST return a value for next steps to use
   ✓ Keep it simple - this is one step in a flow!
   ✓ Focus on a single operation

2. HTTP REQUESTS:
   ✓ Use native fetch API (built-in)
   ✓ NO external HTTP libraries needed (no axios, request, etc.)
   ✓ Simple error handling for responses
   ✓ Always check response.ok before processing
   
   Example:
   ```typescript
   const response = await fetch(url, {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify(data)
   });
   
   if (!response.ok) {
     throw new Error(`API error: ${response.statusText}`);
   }
   
   return await response.json();
   ```

3. INPUT PARAMETERS:
   ✓ Inputs come from previous steps or flow connections
   ✓ Expect tokens/credentials from flow connections
   ✓ NO OAuth flows or token generation in code
   ✓ NO client IDs or secrets in code
   ✓ NO redirect URLs
   ✓ NO environment variables
   ✓ For non-string literal values, wrap in {{ }}: 
     - Numbers: {{ 500 }}
     - Arrays: {{ [1,2,3,4] }}
     - String arrays: {{ ["apple", "banana", "orange"] }}
     - Objects: {{ {"key": "value"} }}
     - Array of objects: {{ [{"key": "value1"}, {"key": "value2"}] }}

4. FLOW INTEGRATION:
   ✓ Return data that next steps can use
   ✓ Keep processing focused on one task
   ✓ Don't try to handle multiple operations
   ✓ Let the flow orchestrate complex processes
   ✓ Think: "What does the NEXT step need from this step?"

5. TITLE GUIDELINES:
   ✓ Title should be 2-4 words, action-oriented
   ✓ Use verb + noun format
   ✓ Examples: "Send Email", "Query Database", "Transform JSON", 
     "Fetch User Data", "Calculate Total", "Filter Records"

📦 OUTPUT FORMAT:

IMPORTANT: Always wrap your response in markdown code blocks for proper display!

For JSON responses, use:
```json
{
  "code": "export const code = async (inputs: { ... }) => { ... }",
  "inputs": [
    {
      "name": "inputName",
      "description": "What this input is for",
      "suggestedValue": "Example or hint for the user"
    }
  ],
  "title": "Action Name"
}
```

For TypeScript code examples, use:
```typescript
export const code = async (inputs: { ... }) => {
  // code here
}
```

This ensures proper syntax highlighting in the UI!

✨ PERFECT EXAMPLES:

Example 1 - API Call with Authentication:
{
  "code": "export const code = async (inputs: { accessToken: string, userId: string }) => {\\n  const response = await fetch(`https://api.example.com/users/${inputs.userId}`, {\\n    headers: {\\n      'Authorization': `Bearer ${inputs.accessToken}`,\\n      'Content-Type': 'application/json'\\n    }\\n  });\\n\\n  if (!response.ok) {\\n    throw new Error(`API error: ${response.statusText}`);\\n  }\\n\\n  const data = await response.json();\\n  return { user: data };\\n}",
  "inputs": [
    {
      "name": "accessToken",
      "description": "API access token from connection",
      "suggestedValue": "Your API access token"
    },
    {
      "name": "userId",
      "description": "User ID to fetch",
      "suggestedValue": "{{ trigger.userId }}"
    }
  ],
  "title": "Fetch User Data"
}

Example 2 - Data Transformation:
{
  "code": "export const code = async (inputs: { items: any[], filterKey: string, filterValue: any }) => {\\n  const filtered = inputs.items.filter(item => \\n    item[inputs.filterKey] === inputs.filterValue\\n  );\\n  \\n  return { \\n    filtered: filtered,\\n    count: filtered.length \\n  };\\n}",
  "inputs": [
    {
      "name": "items",
      "description": "Array of items to filter",
      "suggestedValue": "{{ previousStep.data }}"
    },
    {
      "name": "filterKey",
      "description": "Property name to filter by",
      "suggestedValue": "status"
    },
    {
      "name": "filterValue",
      "description": "Value to match",
      "suggestedValue": "active"
    }
  ],
  "title": "Filter Items"
}

Example 3 - Gmail API (using Google SDK):
{
  "code": "export const code = async (inputs: { accessToken: string }) => {\\n  try {\\n    const auth = new google.auth.OAuth2();\\n    auth.setCredentials({ access_token: inputs.accessToken });\\n\\n    const gmail = google.gmail({ version: 'v1', auth });\\n    const response = await gmail.users.messages.list({\\n      userId: 'me',\\n      maxResults: 10\\n    });\\n\\n    return { messages: response.data.messages || [] };\\n  } catch (error) {\\n    throw new Error(`Gmail API error: ${error.message}`);\\n  }\\n}",
  "inputs": [
    {
      "name": "accessToken",
      "description": "Gmail API access token",
      "suggestedValue": "Your Gmail API access token"
    }
  ],
  "title": "List Gmail Messages"
}

❌ COMMON MISTAKES TO AVOID:

1. DON'T implement OAuth flows in the code
2. DON'T use environment variables for config
3. DON'T try to do multiple operations in one step
4. DON'T use external libraries without checking availability
5. DON'T forget to return data for next steps
6. DON'T use overly complex error handling
7. DON'T make the title too long or vague

✅ BEST PRACTICES:

1. Keep code simple and focused on one task
2. Use TypeScript types for inputs
3. Return meaningful data structures
4. Include helpful input descriptions
5. Use suggestedValue to guide users
6. Handle errors gracefully
7. Think about what the next step needs
8. Remember: This is ONE step in a larger flow
"""
    
    # Add context-specific guidelines
    if context.lower() == "api_call":
        return base_guidelines + """

📡 ADDITIONAL GUIDELINES FOR API CALLS:

1. Authentication patterns:
   - Bearer token: headers: { 'Authorization': `Bearer ${inputs.token}` }
   - API key in header: headers: { 'X-API-Key': inputs.apiKey }
   - Basic auth: headers: { 'Authorization': `Basic ${btoa(inputs.username + ':' + inputs.password)}` }

2. Always validate response status
3. Parse JSON responses properly
4. Return structured data for next steps
5. Use descriptive variable names
"""
    
    elif context.lower() == "data_transform":
        return base_guidelines + """

🔄 ADDITIONAL GUIDELINES FOR DATA TRANSFORMATION:

1. Work with arrays and objects from previous steps
2. Use standard JavaScript methods (map, filter, reduce)
3. Return transformed data in a clear structure
4. Handle empty arrays/null values gracefully
5. Keep transformations simple and readable
"""
    
    return base_guidelines


def _search_with_openai(query: str) -> str:
    """Search using OpenAI's Responses API with web_search tool."""
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Web search is not available (no OpenAI API key configured)."
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Use OpenAI's Responses API with web_search tool
        response = client.responses.create(
            model=os.getenv("MODEL_NAME", "gpt-4o"),
            tools=[{"type": "web_search"}],
            input=query
        )
        
        # Get the output text from the response
        answer = response.output_text
        
        if answer:
            return answer
        else:
            return "No results found from web search."
    
    except Exception as e:
        error_msg = str(e)
        # If Responses API fails, provide helpful guidance
        if "responses" in error_msg.lower() or "404" in error_msg:
            return (
                f"OpenAI Responses API error: {error_msg}\n\n"
                "Note: The Responses API with web_search may not be available for your account yet. "
                "You can switch to Perplexity by setting SEARCH_PROVIDER=perplexity in your .env file."
            )
        return f"OpenAI web search error: {str(e)}"


def _search_with_perplexity(query: str) -> str:
    """Search using Perplexity API."""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        return "Perplexity search is not available (no API key configured). Please set PERPLEXITY_API_KEY in .env file."
    
    try:
        # Perplexity API endpoint
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides concise, accurate answers."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.2,
            "max_tokens": 500
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if answer:
            return answer
        else:
            return "No results found from web search."
    
    except requests.exceptions.Timeout:
        return "Web search timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Perplexity search error: {str(e)}"
    except Exception as e:
        return f"Unexpected error during Perplexity search: {str(e)}"


# Create tool wrappers with langchain decorators only when needed
def get_all_tools():
    """Get all tools as langchain tools with lazy import."""
    from langchain.tools import tool
    
    @tool
    def check_activepieces_tool(query: str) -> str:
        """
        Check if an integration, action, or trigger exists in ActivePieces.
        Use this tool to verify if a specific piece, action, or trigger is available.
        
        Args:
            query: The name of the piece, action, or trigger to check
            
        Returns:
            Information about whether it exists and its details
        """
        return check_activepieces(query)
    
    @tool
    def search_activepieces_docs_tool(query: str) -> str:
        """
        Search the ActivePieces knowledge base for relevant information.
        Use this tool to find information about how to do something, what actions to use,
        or to get contextual information about ActivePieces features.
        
        Args:
            query: The question or topic to search for
            
        Returns:
            Relevant information from the knowledge base
        """
        return search_activepieces_docs(query)
    
    @tool
    def web_search_tool(query: str) -> str:
        """
        Search the web for current information using OpenAI or Perplexity API.
        Use this tool when the information is not available in the ActivePieces knowledge base
        or when you need real-time/current information.
        
        Args:
            query: The search query
            
        Returns:
            Information from the web
        """
        return web_search(query)
    
    @tool
    def get_code_generation_guidelines_tool(context: str = "general") -> str:
        """
        Get comprehensive guidelines for generating TypeScript code for ActivePieces automation flows.
        Use this tool whenever you need to generate or help users write code pieces.
        
        Args:
            context: The type of code to generate (e.g., 'api_call', 'data_transform', 'general')
            
        Returns:
            Detailed guidelines and best practices for code generation
        """
        return get_code_generation_guidelines(context)
    
    return [check_activepieces_tool, search_activepieces_docs_tool, web_search_tool, get_code_generation_guidelines_tool]


# Export all tools (for backward compatibility, lazy)
ALL_TOOLS = None  # Will be populated on first access

