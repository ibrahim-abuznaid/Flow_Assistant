#!/usr/bin/env python3
"""
Generate FAISS vector store from SQLite database.
This replaces the old prepare_knowledge_base.py that used JSON files.
"""
import os
import sys
import pickle
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("\n" + "="*60)
    print("🔧 Creating FAISS Vector Store from SQLite Database")
    print("="*60 + "\n")
    
    # Check if OpenAI API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("Please set your OpenAI API key in .env file")
        return
    
    print("✓ OpenAI API key found")
    
    # Import required libraries
    try:
        import faiss
        from langchain.schema import Document
        from langchain_community.vectorstores import FAISS
        from langchain_community.docstore.in_memory import InMemoryDocstore
        from langchain_openai import OpenAIEmbeddings
        print("✓ Required libraries imported")
    except ImportError as e:
        print(f"❌ ERROR: Missing required library: {e}")
        print("Make sure you've installed all requirements: pip install -r requirements.txt")
        return
    
    # Import database helper
    try:
        from src.activepieces_db import ActivepiecesDB
        print("✓ Database helper imported")
    except ImportError as e:
        print(f"❌ ERROR: Could not import database helper: {e}")
        return
    
    # Load data from SQLite database
    print("\n📊 Loading data from SQLite database...")
    
    documents = []
    
    try:
        with ActivepiecesDB() as db:
            # Get all pieces
            pieces = db.get_all_pieces()
            print(f"✓ Loaded {len(pieces)} pieces")
            
            # Create documents for each piece
            for piece in pieces:
                # Get full details for the piece
                piece_details = db.get_piece_details(piece['name'])
                if not piece_details:
                    continue
                
                # Create main piece document
                description = piece_details.get('description', '') or 'No description available'
                piece_text = f"Piece: {piece_details['display_name']}. Name: {piece_details['name']}. Description: {description}. Authentication: {piece_details.get('auth_type', 'None')}. Categories: {', '.join(piece_details.get('categories', []))}. Actions: {len(piece_details.get('actions', []))}. Triggers: {len(piece_details.get('triggers', []))}"
                
                # Only add if content is valid
                if piece_text and len(piece_text.strip()) > 10:
                    documents.append(Document(
                        page_content=piece_text,
                        metadata={
                            'type': 'piece',
                            'name': piece_details['name'],
                            'display_name': piece_details['display_name']
                        }
                    ))
                
                # Create documents for each action
                for action in piece_details.get('actions', []):
                    desc = action.get('description', '') or 'No description available'
                    action_text = f"Action: {action['display_name']}. Piece: {piece_details['display_name']}. Description: {desc}. Requires Auth: {action.get('requires_auth', False)}"
                    
                    # Only add if content is valid
                    if action_text and len(action_text.strip()) > 10:
                        documents.append(Document(
                            page_content=action_text,
                            metadata={
                                'type': 'action',
                                'piece': piece_details['name'],
                                'action': action['name']
                            }
                        ))
                
                # Create documents for each trigger
                for trigger in piece_details.get('triggers', []):
                    desc = trigger.get('description', '') or 'No description available'
                    trigger_text = f"Trigger: {trigger['display_name']}. Piece: {piece_details['display_name']}. Description: {desc}. Type: {trigger.get('trigger_type', 'Unknown')}. Requires Auth: {trigger.get('requires_auth', False)}"
                    
                    # Only add if content is valid
                    if trigger_text and len(trigger_text.strip()) > 10:
                        documents.append(Document(
                            page_content=trigger_text,
                            metadata={
                                'type': 'trigger',
                                'piece': piece_details['name'],
                                'trigger': trigger['name']
                            }
                        ))
            
            print(f"✓ Created {len(documents)} documents for vector store")
    
    except Exception as e:
        print(f"❌ ERROR loading data from database: {e}")
        return
    
    if not documents:
        print("❌ ERROR: No documents created")
        return
    
    # Create embeddings using langchain's OpenAI embeddings
    print("\n🤖 Creating embeddings...")
    
    try:
        embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model="text-embedding-ada-002"
        )
        print("✓ Embeddings model initialized")
    except Exception as e:
        print(f"❌ ERROR: Could not initialize embeddings: {e}")
        return
    
    # Create FAISS vector store
    print("\n🔍 Creating FAISS vector store...")
    print("⏳ This may take a few minutes (generating embeddings for all documents)...")
    
    try:
        # Create vector store from documents
        vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embeddings
        )
        print(f"✓ FAISS vector store created with {len(documents)} documents")
    except Exception as e:
        print(f"❌ ERROR creating vector store: {e}")
        return
    
    # Save to disk
    print("\n💾 Saving vector store to disk...")
    
    output_dir = project_root / "data" / "ap_faiss_index"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Save FAISS index
        faiss.write_index(vector_store.index, str(output_dir / "index.faiss"))
        print(f"✓ Saved FAISS index to {output_dir / 'index.faiss'}")
        
        # Save docstore and index mapping
        docstore_dict = {}
        for doc_id, doc in vector_store.docstore._dict.items():
            docstore_dict[doc_id] = {
                'page_content': doc.page_content,
                'metadata': doc.metadata
            }
        
        with open(output_dir / "index.pkl", "wb") as f:
            pickle.dump((docstore_dict, vector_store.index_to_docstore_id), f)
        print(f"✓ Saved document store to {output_dir / 'index.pkl'}")
        
    except Exception as e:
        print(f"❌ ERROR saving vector store: {e}")
        return
    
    print("\n" + "="*60)
    print("✅ SUCCESS! Vector store created successfully!")
    print("="*60)
    print(f"\nVector store location: {output_dir}")
    print(f"Documents indexed: {len(documents)}")
    print("\nYou can now start the backend server:")
    print("  uvicorn src.main:app --host 0.0.0.0 --port 8000")
    print("\n")


if __name__ == "__main__":
    main()

