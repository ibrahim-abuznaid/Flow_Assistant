"""
Prepare the knowledge base by creating a FAISS vector store from the Pieces knowledge base.
"""
import json
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

load_dotenv()


def load_pieces_data():
    """Load the Pieces knowledge base JSON file."""
    with open("data/pieces_knowledge_base.json", "r", encoding="utf-8") as f:
        return json.load(f)


def create_documents_from_pieces(pieces_data):
    """Convert Pieces data into Document objects for vector store."""
    documents = []
    
    pieces = pieces_data.get("pieces", [])
    
    for piece in pieces:
        piece_name = piece.get("displayName", "")
        piece_slug = piece.get("slug", "")
        description = piece.get("description", "")
        categories = ", ".join(piece.get("categories", []))
        
        # Create document for the piece itself
        piece_doc = f"""
Piece: {piece_name} ({piece_slug})
Description: {description}
Categories: {categories}
Type: Integration/Piece
"""
        documents.append(Document(
            page_content=piece_doc.strip(),
            metadata={
                "type": "piece",
                "name": piece_name,
                "slug": piece_slug
            }
        ))
        
        # Create documents for each action
        for action in piece.get("actions", []):
            action_name = action.get("displayName", "")
            action_desc = action.get("description", "")
            action_var = action.get("variableName", "")
            
            action_doc = f"""
Action: {action_name}
Piece: {piece_name}
Description: {action_desc}
Variable Name: {action_var}
Type: Action
"""
            documents.append(Document(
                page_content=action_doc.strip(),
                metadata={
                    "type": "action",
                    "piece": piece_name,
                    "action_name": action_name,
                    "slug": piece_slug
                }
            ))
        
        # Create documents for each trigger
        for trigger in piece.get("triggers", []):
            trigger_name = trigger.get("displayName", "")
            trigger_desc = trigger.get("description", "")
            trigger_var = trigger.get("variableName", "")
            
            trigger_doc = f"""
Trigger: {trigger_name}
Piece: {piece_name}
Description: {trigger_desc}
Variable Name: {trigger_var}
Type: Trigger
"""
            documents.append(Document(
                page_content=trigger_doc.strip(),
                metadata={
                    "type": "trigger",
                    "piece": piece_name,
                    "trigger_name": trigger_name,
                    "slug": piece_slug
                }
            ))
    
    return documents


def create_vector_store(documents):
    """Create and save FAISS vector store."""
    print(f"Creating vector store with {len(documents)} documents...")
    
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_documents(documents, embeddings)
    
    # Save to disk
    vector_store.save_local("data/ap_faiss_index")
    print("Vector store created and saved to 'data/ap_faiss_index'")
    
    return vector_store


def main():
    """Main function to prepare the knowledge base."""
    print("Loading Pieces knowledge base...")
    pieces_data = load_pieces_data()
    
    print(f"Total pieces: {pieces_data['metadata']['totalPieces']}")
    print(f"Total actions: {pieces_data['metadata']['totalActions']}")
    print(f"Total triggers: {pieces_data['metadata']['totalTriggers']}")
    
    print("\nCreating documents...")
    documents = create_documents_from_pieces(pieces_data)
    print(f"Created {len(documents)} documents")
    
    print("\nCreating vector store...")
    create_vector_store(documents)
    
    print("\n✓ Knowledge base preparation complete!")


if __name__ == "__main__":
    main()

