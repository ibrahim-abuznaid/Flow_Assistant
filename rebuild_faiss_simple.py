"""
Rebuild the FAISS vector store from PostgreSQL database using a simple approach.
This version uses the openai client directly to avoid version compatibility issues.
"""
import os
import pickle
import numpy as np
from dotenv import load_dotenv
from db_config import get_db_cursor, test_connection
import faiss

load_dotenv()

def fetch_all_pieces_from_db():
    """Fetch all pieces with their actions and triggers from PostgreSQL."""
    pieces_data = []
    
    try:
        with get_db_cursor() as cur:
            # Fetch all pieces
            cur.execute("""
                SELECT 
                    id, name, display_name, description, 
                    categories, auth_type, version
                FROM pieces
                ORDER BY display_name
            """)
            pieces = cur.fetchall()
            
            print(f"Found {len(pieces)} pieces in database")
            
            for piece in pieces:
                piece_id = piece['id']
                
                # Fetch actions for this piece
                cur.execute("""
                    SELECT display_name, name, description, requires_auth
                    FROM actions
                    WHERE piece_id = %s
                    ORDER BY display_name
                """, (piece_id,))
                actions = cur.fetchall()
                
                # Fetch triggers for this piece
                cur.execute("""
                    SELECT display_name, name, description, trigger_type, requires_auth
                    FROM triggers
                    WHERE piece_id = %s
                    ORDER BY display_name
                """, (piece_id,))
                triggers = cur.fetchall()
                
                pieces_data.append({
                    'id': piece['id'],
                    'name': piece['name'],
                    'displayName': piece['display_name'],
                    'description': piece['description'] or '',
                    'categories': piece['categories'] or [],
                    'auth_type': piece['auth_type'],
                    'version': piece['version'],
                    'actions': [
                        {
                            'displayName': a['display_name'],
                            'name': a['name'],
                            'description': a['description'] or '',
                            'requires_auth': a['requires_auth']
                        }
                        for a in actions
                    ],
                    'triggers': [
                        {
                            'displayName': t['display_name'],
                            'name': t['name'],
                            'description': t['description'] or '',
                            'trigger_type': t['trigger_type'],
                            'requires_auth': t['requires_auth']
                        }
                        for t in triggers
                    ]
                })
            
            return pieces_data
            
    except Exception as e:
        print(f"Error fetching pieces from database: {e}")
        raise


def create_text_documents(pieces_data):
    """Convert database pieces into text documents and metadata."""
    documents = []
    metadata_list = []
    
    for piece in pieces_data:
        piece_name = piece.get("displayName", "")
        piece_slug = piece.get("name", "")
        description = piece.get("description", "")
        categories = ", ".join(piece.get("categories", []))
        auth_type = piece.get("auth_type", "")
        
        # Create document for the piece itself
        piece_doc = f"""
Piece: {piece_name} ({piece_slug})
Description: {description}
Categories: {categories}
Authentication: {auth_type}
Type: Integration/Piece
""".strip()
        
        documents.append(piece_doc)
        metadata_list.append({
            "type": "piece",
            "name": piece_name,
            "slug": piece_slug,
            "categories": categories
        })
        
        # Create documents for each action
        for action in piece.get("actions", []):
            action_name = action.get("displayName", "")
            action_desc = action.get("description", "")
            action_var = action.get("name", "")
            requires_auth = action.get("requires_auth", False)
            
            action_doc = f"""
Action: {action_name}
Piece: {piece_name}
Description: {action_desc}
Variable Name: {action_var}
Requires Authentication: {requires_auth}
Type: Action
""".strip()
            
            documents.append(action_doc)
            metadata_list.append({
                "type": "action",
                "piece": piece_name,
                "action_name": action_name,
                "slug": piece_slug,
                "requires_auth": requires_auth
            })
        
        # Create documents for each trigger
        for trigger in piece.get("triggers", []):
            trigger_name = trigger.get("displayName", "")
            trigger_desc = trigger.get("description", "")
            trigger_var = trigger.get("name", "")
            trigger_type = trigger.get("trigger_type", "")
            requires_auth = trigger.get("requires_auth", False)
            
            trigger_doc = f"""
Trigger: {trigger_name}
Piece: {piece_name}
Description: {trigger_desc}
Variable Name: {trigger_var}
Trigger Type: {trigger_type}
Requires Authentication: {requires_auth}
Type: Trigger
""".strip()
            
            documents.append(trigger_doc)
            metadata_list.append({
                "type": "trigger",
                "piece": piece_name,
                "trigger_name": trigger_name,
                "slug": piece_slug,
                "trigger_type": trigger_type,
                "requires_auth": requires_auth
            })
    
    return documents, metadata_list


def get_embeddings_with_openai(texts, api_key, batch_size=100):
    """Get embeddings using OpenAI API directly."""
    import openai
    from openai import _base_client
    
    # Monkey patch to fix proxies parameter issue with older openai versions
    original_init = _base_client.SyncHttpxClientWrapper.__init__
    
    def patched_init(self, **kwargs):
        # Remove unsupported 'proxies' argument if present
        kwargs.pop('proxies', None)
        original_init(self, **kwargs)
    
    _base_client.SyncHttpxClientWrapper.__init__ = patched_init
    
    client = openai.OpenAI(api_key=api_key)
    all_embeddings = []
    
    print(f"Getting embeddings for {len(texts)} documents...")
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}...")
        
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=batch
            )
            
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)
            
        except Exception as e:
            print(f"  Error getting embeddings for batch: {e}")
            raise
    
    return np.array(all_embeddings, dtype=np.float32)


def create_faiss_index(embeddings, metadata_list, texts, index_path="ap_faiss_index"):
    """Create and save FAISS index."""
    dimension = embeddings.shape[1]
    
    # Create FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save index
    os.makedirs(index_path, exist_ok=True)
    faiss.write_index(index, os.path.join(index_path, "index.faiss"))
    
    # Save metadata and texts in the format expected by langchain
    docstore = {
        str(i): {"page_content": texts[i], "metadata": metadata_list[i]}
        for i in range(len(texts))
    }
    
    index_to_docstore_id = {i: str(i) for i in range(len(texts))}
    
    # Save as pickle (langchain format)
    with open(os.path.join(index_path, "index.pkl"), "wb") as f:
        pickle.dump((docstore, index_to_docstore_id), f)
    
    print(f"[OK] FAISS index created and saved to '{index_path}'")
    print(f"   - Index dimension: {dimension}")
    print(f"   - Number of vectors: {index.ntotal}")


def main():
    """Main function to rebuild the FAISS index from PostgreSQL."""
    print("=" * 60)
    print("REBUILDING FAISS INDEX FROM POSTGRESQL DATABASE")
    print("(Simple direct approach)")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[ERROR] OPENAI_API_KEY environment variable not set!")
        print("Please set it in your .env file")
        return
    
    # Test database connection
    print("\n1. Testing database connection...")
    if not test_connection():
        print("\n[ERROR] Could not connect to database.")
        return
    
    # Fetch pieces from database
    print("\n2. Fetching pieces from PostgreSQL...")
    pieces_data = fetch_all_pieces_from_db()
    
    total_actions = sum(len(p.get("actions", [])) for p in pieces_data)
    total_triggers = sum(len(p.get("triggers", [])) for p in pieces_data)
    
    print(f"   [OK] Total pieces: {len(pieces_data)}")
    print(f"   [OK] Total actions: {total_actions}")
    print(f"   [OK] Total triggers: {total_triggers}")
    
    # Create text documents
    print("\n3. Creating text documents...")
    texts, metadata = create_text_documents(pieces_data)
    print(f"   [OK] Created {len(texts)} documents")
    
    # Get embeddings
    print("\n4. Getting embeddings from OpenAI...")
    embeddings = get_embeddings_with_openai(texts, api_key)
    print(f"   [OK] Got {len(embeddings)} embeddings")
    
    # Create and save FAISS index
    print("\n5. Creating FAISS index...")
    create_faiss_index(embeddings, metadata, texts)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] FAISS INDEX REBUILD COMPLETE!")
    print("=" * 60)
    print("\nThe FAISS index has been successfully rebuilt from PostgreSQL data.")
    print("You can now use the assistant with the updated knowledge base.")


if __name__ == "__main__":
    main()

