"""
Rebuild the FAISS vector store with COMPLETE information from PostgreSQL.
This version includes actions/triggers WITH their properties (inputs) and descriptions.
"""
import os
import pickle
import numpy as np
from dotenv import load_dotenv
from db_config import get_db_cursor, test_connection
import faiss

load_dotenv()


def fetch_complete_pieces_from_db():
    """Fetch pieces with ALL details including action/trigger properties."""
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
                
                # Fetch actions with their properties
                cur.execute("""
                    SELECT 
                        a.id, a.name, a.display_name, a.description, 
                        a.requires_auth, a.metadata
                    FROM actions a
                    WHERE a.piece_id = %s
                    ORDER BY a.display_name
                """, (piece_id,))
                actions = cur.fetchall()
                
                # For each action, get its properties
                actions_with_props = []
                for action in actions:
                    cur.execute("""
                        SELECT 
                            property_name, display_name, description,
                            property_type, required, default_value, metadata
                        FROM action_properties
                        WHERE action_id = %s
                        ORDER BY display_name
                    """, (action['id'],))
                    properties = cur.fetchall()
                    
                    # Get options for dropdown properties if any
                    for prop in properties:
                        if prop['property_type'] in ['Dropdown', 'StaticDropdown', 'MultiSelectDropdown']:
                            cur.execute("""
                                SELECT option_label, option_value
                                FROM property_options
                                WHERE property_id = (
                                    SELECT id FROM action_properties 
                                    WHERE action_id = %s AND property_name = %s
                                )
                            """, (action['id'], prop['property_name']))
                            options = cur.fetchall()
                            prop['options'] = [
                                {'label': opt['option_label'], 'value': opt['option_value']}
                                for opt in options
                            ]
                    
                    actions_with_props.append({
                        'id': action['id'],
                        'name': action['name'],
                        'displayName': action['display_name'],
                        'description': action['description'] or '',
                        'requires_auth': action['requires_auth'],
                        'metadata': action['metadata'],
                        'properties': [
                            {
                                'name': p['property_name'],
                                'displayName': p['display_name'],
                                'description': p['description'] or '',
                                'type': p['property_type'],
                                'required': p['required'],
                                'defaultValue': p['default_value'],
                                'options': p.get('options', [])
                            }
                            for p in properties
                        ]
                    })
                
                # Fetch triggers with their properties
                cur.execute("""
                    SELECT 
                        t.id, t.name, t.display_name, t.description,
                        t.trigger_type, t.requires_auth, t.metadata
                    FROM triggers t
                    WHERE t.piece_id = %s
                    ORDER BY t.display_name
                """, (piece_id,))
                triggers = cur.fetchall()
                
                # For each trigger, get its properties
                triggers_with_props = []
                for trigger in triggers:
                    cur.execute("""
                        SELECT 
                            property_name, display_name, description,
                            property_type, required, default_value, metadata
                        FROM trigger_properties
                        WHERE trigger_id = %s
                        ORDER BY display_name
                    """, (trigger['id'],))
                    properties = cur.fetchall()
                    
                    # Get options for dropdown properties if any
                    for prop in properties:
                        if prop['property_type'] in ['Dropdown', 'StaticDropdown', 'MultiSelectDropdown']:
                            cur.execute("""
                                SELECT option_label, option_value
                                FROM property_options
                                WHERE property_id = (
                                    SELECT id FROM trigger_properties 
                                    WHERE trigger_id = %s AND property_name = %s
                                )
                            """, (trigger['id'], prop['property_name']))
                            options = cur.fetchall()
                            prop['options'] = [
                                {'label': opt['option_label'], 'value': opt['option_value']}
                                for opt in options
                            ]
                    
                    triggers_with_props.append({
                        'id': trigger['id'],
                        'name': trigger['name'],
                        'displayName': trigger['display_name'],
                        'description': trigger['description'] or '',
                        'trigger_type': trigger['trigger_type'],
                        'requires_auth': trigger['requires_auth'],
                        'metadata': trigger['metadata'],
                        'properties': [
                            {
                                'name': p['property_name'],
                                'displayName': p['display_name'],
                                'description': p['description'] or '',
                                'type': p['property_type'],
                                'required': p['required'],
                                'defaultValue': p['default_value'],
                                'options': p.get('options', [])
                            }
                            for p in properties
                        ]
                    })
                
                pieces_data.append({
                    'id': piece['id'],
                    'name': piece['name'],
                    'displayName': piece['display_name'],
                    'description': piece['description'] or '',
                    'categories': piece['categories'] or [],
                    'auth_type': piece['auth_type'],
                    'version': piece['version'],
                    'actions': actions_with_props,
                    'triggers': triggers_with_props
                })
            
            return pieces_data
            
    except Exception as e:
        print(f"Error fetching pieces from database: {e}")
        raise


def create_rich_documents(pieces_data):
    """Convert pieces into rich text documents with ALL details."""
    documents = []
    metadata_list = []
    
    total_properties = 0
    
    for piece in pieces_data:
        piece_name = piece.get("displayName", "")
        piece_slug = piece.get("name", "")
        description = piece.get("description", "")
        categories = ", ".join(piece.get("categories", []))
        auth_type = piece.get("auth_type", "")
        
        # Create document for the piece itself
        piece_doc = f"""Piece: {piece_name} ({piece_slug})
Description: {description}
Categories: {categories}
Authentication: {auth_type}
Type: Integration/Piece"""
        
        documents.append(piece_doc)
        metadata_list.append({
            "type": "piece",
            "name": piece_name,
            "slug": piece_slug,
            "categories": categories
        })
        
        # Create RICH documents for each action with properties
        for action in piece.get("actions", []):
            action_name = action.get("displayName", "")
            action_desc = action.get("description", "")
            action_var = action.get("name", "")
            requires_auth = action.get("requires_auth", False)
            properties = action.get("properties", [])
            
            # Build detailed property information
            property_details = []
            if properties:
                property_details.append("\n\nINPUT PROPERTIES:")
                for prop in properties:
                    prop_name = prop.get("displayName", "")
                    prop_desc = prop.get("description", "")
                    prop_type = prop.get("type", "")
                    prop_required = "Required" if prop.get("required") else "Optional"
                    prop_default = prop.get("defaultValue", "")
                    
                    prop_detail = f"\n  - {prop_name} ({prop_type}, {prop_required})"
                    if prop_desc:
                        prop_detail += f"\n    Description: {prop_desc}"
                    if prop_default:
                        prop_detail += f"\n    Default: {prop_default}"
                    
                    # Add options if it's a dropdown
                    options = prop.get("options", [])
                    if options:
                        prop_detail += "\n    Options: " + ", ".join([opt['label'] for opt in options[:10]])
                        if len(options) > 10:
                            prop_detail += f" ...and {len(options) - 10} more"
                    
                    property_details.append(prop_detail)
                    total_properties += 1
            
            action_doc = f"""Action: {action_name}
Piece: {piece_name}
Description: {action_desc}
Variable Name: {action_var}
Requires Authentication: {requires_auth}
Type: Action{''.join(property_details)}"""
            
            documents.append(action_doc)
            metadata_list.append({
                "type": "action",
                "piece": piece_name,
                "action_name": action_name,
                "slug": piece_slug,
                "requires_auth": requires_auth,
                "num_properties": len(properties)
            })
        
        # Create RICH documents for each trigger with properties
        for trigger in piece.get("triggers", []):
            trigger_name = trigger.get("displayName", "")
            trigger_desc = trigger.get("description", "")
            trigger_var = trigger.get("name", "")
            trigger_type = trigger.get("trigger_type", "")
            requires_auth = trigger.get("requires_auth", False)
            properties = trigger.get("properties", [])
            
            # Build detailed property information
            property_details = []
            if properties:
                property_details.append("\n\nCONFIGURATION PROPERTIES:")
                for prop in properties:
                    prop_name = prop.get("displayName", "")
                    prop_desc = prop.get("description", "")
                    prop_type = prop.get("type", "")
                    prop_required = "Required" if prop.get("required") else "Optional"
                    prop_default = prop.get("defaultValue", "")
                    
                    prop_detail = f"\n  - {prop_name} ({prop_type}, {prop_required})"
                    if prop_desc:
                        prop_detail += f"\n    Description: {prop_desc}"
                    if prop_default:
                        prop_detail += f"\n    Default: {prop_default}"
                    
                    # Add options if it's a dropdown
                    options = prop.get("options", [])
                    if options:
                        prop_detail += "\n    Options: " + ", ".join([opt['label'] for opt in options[:10]])
                        if len(options) > 10:
                            prop_detail += f" ...and {len(options) - 10} more"
                    
                    property_details.append(prop_detail)
                    total_properties += 1
            
            trigger_doc = f"""Trigger: {trigger_name}
Piece: {piece_name}
Description: {trigger_desc}
Variable Name: {trigger_var}
Trigger Type: {trigger_type}
Requires Authentication: {requires_auth}
Type: Trigger{''.join(property_details)}"""
            
            documents.append(trigger_doc)
            metadata_list.append({
                "type": "trigger",
                "piece": piece_name,
                "trigger_name": trigger_name,
                "slug": piece_slug,
                "trigger_type": trigger_type,
                "requires_auth": requires_auth,
                "num_properties": len(properties)
            })
    
    print(f"   [OK] Included {total_properties} total properties (inputs) in documents")
    return documents, metadata_list


def get_embeddings_with_openai(texts, api_key, batch_size=100):
    """Get embeddings using OpenAI API directly."""
    import openai
    from openai import _base_client
    
    # Monkey patch to fix proxies parameter issue with older openai versions
    original_init = _base_client.SyncHttpxClientWrapper.__init__
    
    def patched_init(self, **kwargs):
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
    
    # Save metadata and texts in langchain format
    docstore = {
        str(i): {"page_content": texts[i], "metadata": metadata_list[i]}
        for i in range(len(texts))
    }
    
    index_to_docstore_id = {i: str(i) for i in range(len(texts))}
    
    with open(os.path.join(index_path, "index.pkl"), "wb") as f:
        pickle.dump((docstore, index_to_docstore_id), f)
    
    print(f"[OK] FAISS index created and saved to '{index_path}'")
    print(f"   - Index dimension: {dimension}")
    print(f"   - Number of vectors: {index.ntotal}")


def main():
    """Main function to rebuild the FAISS index with complete information."""
    print("=" * 60)
    print("REBUILDING FAISS INDEX - ENHANCED VERSION")
    print("(Includes ALL properties and detailed descriptions)")
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
    
    # Fetch complete pieces with properties
    print("\n2. Fetching COMPLETE data from PostgreSQL...")
    print("   (This includes all actions, triggers, and their properties)")
    pieces_data = fetch_complete_pieces_from_db()
    
    total_actions = sum(len(p.get("actions", [])) for p in pieces_data)
    total_triggers = sum(len(p.get("triggers", [])) for p in pieces_data)
    total_action_props = sum(
        len(action.get("properties", []))
        for p in pieces_data
        for action in p.get("actions", [])
    )
    total_trigger_props = sum(
        len(trigger.get("properties", []))
        for p in pieces_data
        for trigger in p.get("triggers", [])
    )
    
    print(f"   [OK] Total pieces: {len(pieces_data)}")
    print(f"   [OK] Total actions: {total_actions}")
    print(f"   [OK] Total triggers: {total_triggers}")
    print(f"   [OK] Total action properties: {total_action_props}")
    print(f"   [OK] Total trigger properties: {total_trigger_props}")
    
    # Create rich documents
    print("\n3. Creating rich documents with ALL details...")
    texts, metadata = create_rich_documents(pieces_data)
    print(f"   [OK] Created {len(texts)} detailed documents")
    
    # Get embeddings
    print("\n4. Getting embeddings from OpenAI...")
    embeddings = get_embeddings_with_openai(texts, api_key)
    print(f"   [OK] Got {len(embeddings)} embeddings")
    
    # Create and save FAISS index
    print("\n5. Creating FAISS index...")
    create_faiss_index(embeddings, metadata, texts)
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ENHANCED FAISS INDEX REBUILD COMPLETE!")
    print("=" * 60)
    print("\nThe FAISS index now includes:")
    print("  - All piece information")
    print("  - All action/trigger descriptions")
    print("  - ALL INPUT PROPERTIES with types and requirements")
    print("  - Property options for dropdowns")
    print("  - Default values")
    print("\nThe agent now has FULL CONTEXT to guide users!")


if __name__ == "__main__":
    main()

