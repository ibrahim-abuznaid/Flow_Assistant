"""
Tools for the AI assistant agent.
"""
import os
import requests
from typing import Optional, List, Dict, Any
from src.db_config import get_db_cursor
from src.activepieces_db import ActivepiecesDB
from src.query_utils import generate_query_variants, normalize_query


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


def find_action_by_name(action_name: str, limit: int = 50) -> List[Dict[str, str]]:
    """Find which pieces have an action with the given name from SQLite database."""
    action_lower = action_name.lower()
    
    try:
        with ActivepiecesDB() as db:
            try:
                max_results = int(limit)
            except (TypeError, ValueError):
                max_results = 50
            max_results = max(1, min(max_results, 50))
            results = db.search_actions(action_lower, limit=max_results)
            
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


def find_trigger_by_name(trigger_name: str, limit: int = 50) -> List[Dict[str, str]]:
    """Find which pieces have a trigger with the given name from SQLite database."""
    trigger_lower = trigger_name.lower()
    
    try:
        with ActivepiecesDB() as db:
            # Use the search functionality - search in actions will also find triggers
            # Since the helper doesn't have a search_triggers method, we'll query directly
            with get_db_cursor() as cur:
                try:
                    max_results = int(limit)
                except (TypeError, ValueError):
                    max_results = 50
                max_results = max(1, min(max_results, 50))
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
                    LIMIT ?
                """, (f'%{trigger_lower}%', f'%{trigger_lower}%', max_results))
                
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


def list_piece_actions_and_triggers(piece_name: str) -> str:
    """Return formatted list of all actions and triggers for a specific piece."""
    if not piece_name or not piece_name.strip():
        return "Please provide the name of an integration/piece to look up."

    normalized_name = piece_name.strip()

    try:
        piece = find_piece_by_name(normalized_name)
    except Exception as exc:  # pragma: no cover - defensive path for DB issues
        return (
            f"⚠️ Database connection failed while looking up '{normalized_name}'."
            "\nPlease verify the database is accessible and try again."
        )

    if not piece:
        return (
            f"✗ No ActivePieces integration matched '{normalized_name}'."
            "\nTry another name or confirm the piece exists in your workspace."
        )

    display_name = piece.get('displayName') or normalized_name
    description = (piece.get('description') or '').strip()
    actions = piece.get('actions') or []
    triggers = piece.get('triggers') or []

    lines = [f"{display_name} actions and triggers"]
    if description:
        lines.append(description)

    if actions:
        lines.append("")
        lines.append(f"Actions ({len(actions)}):")
        for action in actions:
            title = (action.get('displayName') or action.get('name') or '').strip()
            if not title:
                title = "Unnamed action"
            action_desc = (action.get('description') or '').strip()
            if action_desc:
                lines.append(f"- {title}: {action_desc}")
            else:
                lines.append(f"- {title}")
    else:
        lines.append("")
        lines.append("Actions: None available.")

    if triggers:
        lines.append("")
        lines.append(f"Triggers ({len(triggers)}):")
        for trigger in triggers:
            title = (trigger.get('displayName') or trigger.get('name') or '').strip()
            if not title:
                title = "Unnamed trigger"
            trigger_desc = (trigger.get('description') or '').strip()
            if trigger_desc:
                lines.append(f"- {title}: {trigger_desc}")
            else:
                lines.append(f"- {title}")
    else:
        lines.append("")
        lines.append("Triggers: None available.")

    return "\n".join(lines).strip()


def list_action_inputs(piece_name: str, action_name: str) -> str:
    """Return input schema for a specific action of a piece."""
    if not piece_name or not piece_name.strip() or not action_name or not action_name.strip():
        return "Please provide both the integration name and the action name."

    piece_query = piece_name.strip()
    action_query = action_name.strip()

    try:
        piece = find_piece_by_name(piece_query)
    except Exception:
        return (
            f"⚠️ Database connection failed while looking up '{piece_query}'."
            "\nPlease verify the database is accessible and try again."
        )

    if not piece:
        return (
            f"✗ No ActivePieces integration matched '{piece_query}'."
            "\nDouble-check the integration name and try again."
        )

    canonical_piece_name = piece.get('name') or piece_query

    try:
        with ActivepiecesDB() as db:
            detailed_piece = db.get_piece_details(canonical_piece_name.lower())
    except Exception:
        return (
            f"⚠️ Failed to load action details for '{piece_query}'."
            "\nPlease ensure the database is accessible."
        )

    if not detailed_piece:
        return (
            f"✗ Unable to load detailed metadata for integration '{piece_query}'."
            "\nIt may have been removed or renamed in the database."
        )

    actions = detailed_piece.get('actions') or []
    action_lower = action_query.lower()

    matched_action = None
    for action in actions:
        display = (action.get('display_name') or action.get('displayName') or '').strip()
        slug = (action.get('name') or '').strip()
        if display.lower() == action_lower or slug.lower() == action_lower:
            matched_action = action
            break

    if not matched_action:
        for action in actions:
            display = (action.get('display_name') or action.get('displayName') or '').strip().lower()
            if action_lower in display and display:
                matched_action = action
                break

    if not matched_action:
        available_names = sorted(
            {
                (a.get('display_name') or a.get('displayName') or a.get('name') or '').strip()
                for a in actions
                if (a.get('display_name') or a.get('displayName') or a.get('name'))
            }
        )
        if available_names:
            available = ", ".join(name for name in available_names if name)
        else:
            available = ""
        if available:
            return (
                f"The integration '{piece.get('displayName') or canonical_piece_name}' does not have an action matching '{action_query}'."
                f"\nAvailable actions include: {available}"
            )
        return (
            f"The integration '{piece.get('displayName') or canonical_piece_name}' has no registered actions."
        )

    action_slug = (matched_action.get('name') or '').strip()
    action_display_name = (
        matched_action.get('display_name')
        or matched_action.get('displayName')
        or action_slug
        or action_query
    ).strip()
    action_description = (matched_action.get('description') or '').strip()

    if not action_slug:
        return (
            f"Unable to locate the internal identifier for action '{action_display_name}'."
            "\nPlease try another action."
        )

    try:
        with ActivepiecesDB() as db:
            inputs = db.get_action_inputs(canonical_piece_name.lower(), action_slug)
    except Exception:
        return (
            f"⚠️ Failed to retrieve inputs for '{action_display_name}'."
            "\nPlease ensure the database is accessible."
        )

    lines = [f"{piece.get('displayName') or canonical_piece_name} – {action_display_name} inputs"]
    if action_description:
        lines.append(action_description)

    if not inputs:
        lines.append("")
        lines.append("This action has no configurable inputs.")
        return "\n".join(lines).strip()

    lines.append("")
    for prop in inputs:
        display = (prop.get('display_name') or prop.get('name') or '').strip() or 'Unnamed input'
        input_type = (prop.get('type') or 'unknown').strip()
        required = bool(prop.get('required'))
        description = (prop.get('description') or '').strip()
        default_value = prop.get('default_value')

        requirement = 'required' if required else 'optional'
        lines.append(f"- {display} [{requirement}, {input_type}]")
        if description:
            lines.append(f"  {description}")
        if default_value not in (None, ""):
            lines.append(f"  Default: {default_value}")
    
    return "\n".join(lines).strip()


def search_piece_catalog(query: str = "", auth_type: str = "", limit: int = 10) -> str:
    """Search the pieces catalog with optional auth type filtering."""
    try:
        limit_value = int(limit)
    except (TypeError, ValueError):
        limit_value = 10
    limit_value = max(1, min(limit_value, 50))

    search_query = (query or "").strip()
    auth_display = (auth_type or "").strip()
    auth_filter = auth_display.lower()

    try:
        with ActivepiecesDB() as db:
            results: List[Dict[str, Any]]
            if search_query:
                results = db.search_pieces(search_query, limit=limit_value)
            else:
                results = db.get_all_pieces()
                if auth_filter:
                    results = [
                        row for row in results
                        if (row.get('auth_type') or '').lower() == auth_filter
                    ]
                results = results[:limit_value]

            if auth_filter and search_query:
                results = [
                    row for row in results
                    if (row.get('auth_type') or '').lower() == auth_filter
                ]
    except Exception:
        return "⚠️ Failed to query the pieces catalog. Please confirm database connectivity."

    if not results:
        scope = f" with auth type '{auth_display or auth_filter}'" if auth_filter else ""
        if search_query:
            return f"No pieces matched '{search_query}'{scope}."
        return f"No pieces found{scope}."

    if search_query and auth_filter:
        header = f"Pieces matching '{search_query}' (auth type: {auth_display}):"
    elif search_query:
        header = f"Pieces matching '{search_query}':"
    elif auth_filter:
        header = f"Pieces (auth type: {auth_display}):"
    else:
        header = "Pieces catalog results:"

    lines = [header]
    for idx, row in enumerate(results, 1):
        display = row.get('display_name') or row.get('name') or 'Unnamed piece'
        auth_label = row.get('auth_type') or 'No Auth'
        action_count = row.get('action_count') if row.get('action_count') is not None else len(row.get('actions', []) or [])
        trigger_count = row.get('trigger_count') if row.get('trigger_count') is not None else len(row.get('triggers', []) or [])
        description = (row.get('description') or '').strip()
        lines.append(f"{idx}. {display} — auth: {auth_label}, {action_count} actions, {trigger_count} triggers")
        if description:
            lines.append(f"   {description}")

    return "\n".join(lines).strip()


def get_top_pieces_overview(limit: int = 10) -> str:
    """List the most capable pieces ordered by total actions and triggers."""
    try:
        limit_value = int(limit)
    except (TypeError, ValueError):
        limit_value = 10
    limit_value = max(1, min(limit_value, 50))

    try:
        with ActivepiecesDB() as db:
            rows = db.get_top_pieces(limit_value)
    except Exception:
        return "⚠️ Unable to load top pieces overview. Please check database connectivity."

    if not rows:
        return "No pieces with actions or triggers were found."

    lines = ["Most capable pieces:"]
    for idx, row in enumerate(rows, 1):
        display = row.get('display_name') or 'Unnamed piece'
        auth_label = row.get('auth_type') or 'No Auth'
        action_count = row.get('action_count') or 0
        trigger_count = row.get('trigger_count') or 0
        total = row.get('total_capabilities') or (action_count + trigger_count)
        lines.append(f"{idx}. {display} — auth: {auth_label}, actions: {action_count}, triggers: {trigger_count}, total: {total}")

    return "\n".join(lines).strip()


def list_pieces_by_auth_type(auth_type: str, limit: int = 25) -> str:
    """List pieces that use a specific authentication type."""
    if not auth_type or not auth_type.strip():
        return "Please provide an authentication type (e.g., OAuth2, ApiKey, SecretText)."

    try:
        limit_value = int(limit)
    except (TypeError, ValueError):
        limit_value = 25
    limit_value = max(1, min(limit_value, 100))

    auth_filter = auth_type.strip().lower()

    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT display_name, auth_type, action_count, trigger_count
                FROM pieces_with_capabilities
                WHERE LOWER(auth_type) = ?
                ORDER BY (action_count + trigger_count) DESC, display_name
                LIMIT ?
                """,
                (auth_filter, limit_value),
            )
            rows = cur.fetchall()
    except Exception:
        return "⚠️ Failed to load pieces by authentication type. Please verify the database connection."

    if not rows:
        return f"No pieces found with auth type '{auth_type}'."

    lines = [f"Pieces using auth type '{auth_type}':"]
    for idx, row in enumerate(rows, 1):
        display = row['display_name'] or 'Unnamed piece'
        action_count = row['action_count'] or 0
        trigger_count = row['trigger_count'] or 0
        lines.append(f"{idx}. {display} — {action_count} actions, {trigger_count} triggers")

    return "\n".join(lines).strip()


def search_actions_by_keyword(keyword: str, limit: int = 10) -> str:
    """Search for actions across pieces by keyword."""
    if not keyword or not keyword.strip():
        return "Please provide a keyword to search for actions."

    try:
        results = find_action_by_name(keyword, limit=limit)
    except Exception:
        return "⚠️ Failed to search actions. Please verify the database connection."

    if not results:
        return f"No actions matched '{keyword}'."

    lines = [f"Actions matching '{keyword}':"]
    for idx, action in enumerate(results, 1):
        title = action.get('action') or 'Unnamed action'
        piece_name = action.get('piece') or 'Unknown integration'
        description = (action.get('description') or '').strip()
        lines.append(f"{idx}. {title} — in {piece_name}")
        if description:
            lines.append(f"   {description}")

    return "\n".join(lines).strip()


def search_triggers_by_keyword(keyword: str, limit: int = 10) -> str:
    """Search for triggers across pieces by keyword."""
    if not keyword or not keyword.strip():
        return "Please provide a keyword to search for triggers."

    try:
        results = find_trigger_by_name(keyword, limit=limit)
    except Exception:
        return "⚠️ Failed to search triggers. Please verify the database connection."

    if not results:
        return f"No triggers matched '{keyword}'."

    lines = [f"Triggers matching '{keyword}':"]
    for idx, trigger in enumerate(results, 1):
        title = trigger.get('trigger') or 'Unnamed trigger'
        piece_name = trigger.get('piece') or 'Unknown integration'
        description = (trigger.get('description') or '').strip()
        lines.append(f"{idx}. {title} — in {piece_name}")
        if description:
            lines.append(f"   {description}")

    return "\n".join(lines).strip()


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
        normalized_query = normalize_query(query)
        if not normalized_query:
            return "No query provided for documentation search."

        try:
            per_variant_k = max(1, int(os.getenv("DOC_SEARCH_PER_VARIANT", "4")))
        except ValueError:
            per_variant_k = 4

        try:
            max_results = max(1, int(os.getenv("DOC_SEARCH_MAX_RESULTS", "8")))
        except ValueError:
            max_results = 8

        vector_store = get_vector_store()
        query_variants = generate_query_variants(normalized_query)

        aggregated: Dict[str, Dict[str, Any]] = {}

        for variant in query_variants:
            try:
                variant_results = vector_store.similarity_search_with_score(variant, k=per_variant_k)
            except AttributeError:
                # Fallback if the vector store implementation does not support returning scores
                raw_results = vector_store.similarity_search(variant, k=per_variant_k)
                variant_results = [(doc, None) for doc in raw_results]

            for doc, score in variant_results:
                key = f"{doc.metadata.get('source', '')}|{doc.page_content[:200]}"
                stored = aggregated.get(key)
                if stored is None or (
                    score is not None
                    and (stored["score"] is None or score < stored["score"])
                ):
                    aggregated[key] = {
                        "doc": doc,
                        "score": score,
                        "variant": variant,
                    }

        if not aggregated:
            return "No relevant information found in the knowledge base."

        ranked_results = sorted(
            aggregated.values(),
            key=lambda item: item["score"] if item["score"] is not None else float("inf")
        )

        snippets = []
        snippets.append("Query variants (query fusion):")
        for variant in query_variants:
            snippets.append(f"- {variant}")
        snippets.append("")

        for i, item in enumerate(ranked_results[:max_results], 1):
            doc = item["doc"]
            score = item["score"]
            variant = item["variant"]
            score_text = f"Score: {score:.4f}\n" if isinstance(score, (int, float)) else ""
            snippets.append(f"Result {i} (query variant: {variant})\n{score_text}{doc.page_content}\n")

        return "\n".join(snippets).strip()

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
        """Check if an integration, action, or trigger exists in ActivePieces. Use this to verify availability.
        
        Args:
            query (str): Name of the piece, action, or trigger to check"""
        return check_activepieces(query)
    
    @tool
    def list_piece_actions_and_triggers_tool(piece_name: str) -> str:
        """List all actions and triggers for an ActivePieces integration.
        
        Args:
            piece_name (str): Display name or slug of the integration (e.g., 'Slack')"""
        return list_piece_actions_and_triggers(piece_name)
    
    @tool
    def list_action_inputs_tool(piece_name: str, action_name: str) -> str:
        """List the input fields required for a specific action within an integration.
        
        Args:
            piece_name (str): Display name or slug of the integration (e.g., 'Slack')
            action_name (str): Display name or slug of the action (e.g., 'Send Message')"""
        return list_action_inputs(piece_name, action_name)
    
    @tool
    def search_piece_catalog_tool(query: str = "", auth_type: str = "", limit: int = 10) -> str:
        """Search the catalog of integrations with optional auth-type filtering.
        
        Args:
            query (str): Keywords to match (e.g., 'CRM')
            auth_type (str): Optional authentication type filter (e.g., 'OAuth2')
            limit (int): Maximum number of results to return"""
        return search_piece_catalog(query=query, auth_type=auth_type, limit=limit)
    
    @tool
    def get_top_pieces_overview_tool(limit: int = 10) -> str:
        """Highlight the integrations with the largest number of actions and triggers.
        
        Args:
            limit (int): Maximum number of pieces to list"""
        return get_top_pieces_overview(limit=limit)
    
    @tool
    def list_pieces_by_auth_type_tool(auth_type: str, limit: int = 25) -> str:
        """List integrations that use a specific authentication mechanism.
        
        Args:
            auth_type (str): Authentication type (e.g., 'OAuth2', 'ApiKey')
            limit (int): Maximum number of pieces to list"""
        return list_pieces_by_auth_type(auth_type, limit=limit)
    
    @tool
    def search_actions_by_keyword_tool(keyword: str, limit: int = 10) -> str:
        """Search across all integrations for actions matching the provided keyword.
        
        Args:
            keyword (str): Action keyword (e.g., 'create task')
            limit (int): Maximum number of actions to return"""
        return search_actions_by_keyword(keyword, limit=limit)
    
    @tool
    def search_triggers_by_keyword_tool(keyword: str, limit: int = 10) -> str:
        """Search across all integrations for triggers matching the provided keyword.
        
        Args:
            keyword (str): Trigger keyword (e.g., 'new message')
            limit (int): Maximum number of triggers to return"""
        return search_triggers_by_keyword(keyword, limit=limit)
    
    @tool
    def search_activepieces_docs_tool(query: str) -> str:
        """Search the ActivePieces knowledge base for information about actions, triggers, and their properties.
        
        Args:
            query (str): The question or topic to search for (e.g., 'Slack send message input properties')"""
        return search_activepieces_docs(query)
    
    @tool
    def web_search_tool(query: str) -> str:
        """Search the web for current information not available in ActivePieces knowledge base.
        
        Args:
            query (str): The search query"""
        return web_search(query)
    
    @tool
    def get_code_generation_guidelines_tool(context: str = "general") -> str:
        """Get guidelines for generating TypeScript code for ActivePieces flows. Use before writing code.
        
        Args:
            context (str): Type of code - 'api_call', 'data_transform', or 'general'"""
        return get_code_generation_guidelines(context)
    
    return [
        check_activepieces_tool,
        list_piece_actions_and_triggers_tool,
        list_action_inputs_tool,
        search_piece_catalog_tool,
        get_top_pieces_overview_tool,
        list_pieces_by_auth_type_tool,
        search_actions_by_keyword_tool,
        search_triggers_by_keyword_tool,
        search_activepieces_docs_tool,
        web_search_tool,
        get_code_generation_guidelines_tool,
    ]


# Export all tools (for backward compatibility, lazy)
ALL_TOOLS = None  # Will be populated on first access

