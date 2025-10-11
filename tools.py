"""
Tools for the AI assistant agent.
"""
import os
import requests
from typing import Optional, List, Dict, Any
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from db_config import get_db_cursor


# Global variables for caching
_vector_store = None
_embeddings = None


def get_vector_store():
    """Load or return cached vector store."""
    global _vector_store, _embeddings
    if _vector_store is None:
        import pickle
        import faiss
        from langchain_community.docstore.in_memory import InMemoryDocstore
        from langchain.schema import Document
        
        # Load the FAISS index
        index = faiss.read_index("ap_faiss_index/index.faiss")
        
        # Load the docstore and index mapping
        with open("ap_faiss_index/index.pkl", "rb") as f:
            docstore_dict, index_to_docstore_id = pickle.load(f)
        
        # Convert dict docstore to InMemoryDocstore with Document objects
        documents = {}
        for doc_id, doc_data in docstore_dict.items():
            documents[doc_id] = Document(
                page_content=doc_data['page_content'],
                metadata=doc_data['metadata']
            )
        
        docstore = InMemoryDocstore(documents)
        
        # Initialize embeddings with API key to avoid proxy issues
        import os
        from openai import _base_client
        
        # Monkey patch to fix proxies parameter issue
        original_init = _base_client.SyncHttpxClientWrapper.__init__
        def patched_init(self, **kwargs):
            kwargs.pop('proxies', None)
            original_init(self, **kwargs)
        _base_client.SyncHttpxClientWrapper.__init__ = patched_init
        
        api_key = os.getenv("OPENAI_API_KEY")
        _embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
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
    """Find a piece by name (case-insensitive, prioritizing exact matches) from PostgreSQL."""
    name_lower = name.lower().strip()
    
    try:
        with get_db_cursor() as cur:
            # First, try exact match
            cur.execute("""
                SELECT 
                    id, name, display_name, description, 
                    categories, auth_type, version
                FROM pieces
                WHERE LOWER(display_name) = %s OR LOWER(name) = %s
                LIMIT 1
            """, (name_lower, name_lower))
            
            piece = cur.fetchone()
            
            # If no exact match, try partial match
            if not piece:
                cur.execute("""
                    SELECT 
                        id, name, display_name, description, 
                        categories, auth_type, version
                    FROM pieces
                    WHERE 
                        LOWER(display_name) LIKE %s 
                        OR LOWER(name) LIKE %s
                        OR LOWER(display_name) LIKE %s
                        OR LOWER(name) LIKE %s
                    LIMIT 1
                """, (f'{name_lower}%', f'{name_lower}%', f'%{name_lower}%', f'%{name_lower}%'))
                
                piece = cur.fetchone()
            
            if not piece:
                return None
            
            # Get actions for this piece
            cur.execute("""
                SELECT display_name, description, requires_auth
                FROM actions
                WHERE piece_id = %s
                ORDER BY display_name
            """, (piece['id'],))
            actions = cur.fetchall()
            
            # Get triggers for this piece
            cur.execute("""
                SELECT display_name, description, trigger_type, requires_auth
                FROM triggers
                WHERE piece_id = %s
                ORDER BY display_name
            """, (piece['id'],))
            triggers = cur.fetchall()
            
            # Format result similar to JSON structure
            return {
                'displayName': piece['display_name'],
                'name': piece['name'],
                'slug': piece['name'],
                'description': piece['description'] or '',
                'categories': piece['categories'] or [],
                'auth_type': piece['auth_type'],
                'version': piece['version'],
                'actions': [{'displayName': a['display_name'], 'description': a['description'] or ''} for a in actions],
                'triggers': [{'displayName': t['display_name'], 'description': t['description'] or ''} for t in triggers]
            }
            
    except Exception as e:
        print(f"Error finding piece: {e}")
        return None


def find_action_by_name(action_name: str) -> List[Dict[str, str]]:
    """Find which pieces have an action with the given name from PostgreSQL."""
    action_lower = action_name.lower()
    results = []
    
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    p.display_name as piece,
                    a.display_name as action,
                    a.description
                FROM actions a
                JOIN pieces p ON a.piece_id = p.id
                WHERE 
                    LOWER(a.display_name) LIKE %s 
                    OR LOWER(a.name) LIKE %s
                ORDER BY p.display_name, a.display_name
            """, (f'%{action_lower}%', f'%{action_lower}%'))
            
            results = cur.fetchall()
            
            # Convert to list of dicts
            return [
                {
                    'piece': row['piece'],
                    'action': row['action'],
                    'description': row['description'] or ''
                }
                for row in results
            ]
            
    except Exception as e:
        print(f"Error finding actions: {e}")
        return []


def find_trigger_by_name(trigger_name: str) -> List[Dict[str, str]]:
    """Find which pieces have a trigger with the given name from PostgreSQL."""
    trigger_lower = trigger_name.lower()
    results = []
    
    try:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    p.display_name as piece,
                    t.display_name as trigger,
                    t.description
                FROM triggers t
                JOIN pieces p ON t.piece_id = p.id
                WHERE 
                    LOWER(t.display_name) LIKE %s 
                    OR LOWER(t.name) LIKE %s
                ORDER BY p.display_name, t.display_name
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


@tool
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
    
    # Try to find as a piece
    piece = find_piece_by_name(query)
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


@tool
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
        results = vector_store.similarity_search(query, k=4)
        
        if not results:
            return "No relevant information found in the knowledge base."
        
        # Format results
        snippets = []
        for i, doc in enumerate(results, 1):
            snippets.append(f"Result {i}:\n{doc.page_content}\n")
        
        return "\n".join(snippets)
    
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"


@tool
def web_search(query: str) -> str:
    """
    Search the web for current information using Perplexity API.
    Use this tool when the information is not available in the ActivePieces knowledge base
    or when you need real-time/current information.
    
    Args:
        query: The search query
        
    Returns:
        Information from the web
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        return "Web search is not available (no API key configured)."
    
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
        return f"Web search error: {str(e)}"
    except Exception as e:
        return f"Unexpected error during web search: {str(e)}"


# Export all tools
ALL_TOOLS = [check_activepieces, search_activepieces_docs, web_search]

