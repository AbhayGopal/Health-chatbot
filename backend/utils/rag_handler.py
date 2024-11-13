from typing import List, Dict
import chromadb
import os

class RAGHandler:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    def get_relevant_context(self, query: str) -> str:
        """
        Get relevant context from the database based on the query
        """
        try:
            print("\n=== RAG Debug: Starting Context Retrieval ===")
            print(f"User Query: {query}")
            
            # Get relevant content using semantic search
            relevant_content = self.db_manager.get_relevant_content(query, limit=3)
            
            # Extract health tips and products
            health_tips = relevant_content['health_tips']
            products = relevant_content['products']
            
            print("\nRetrieved Health Tips:")
            for tip in health_tips['documents']:
                print(f"- {tip}")
            
            print("\nRetrieved Products:")
            for doc, meta in zip(products['documents'], products['metadatas']):
                print(f"- {meta.get('name', 'Unknown')}: {doc}")
            
            # Combine context
            context = []
            
            # Add health tips to context
            for tip in health_tips['documents']:
                context.append(f"Health Tip: {tip}")
            
            # Add products to context
            for doc, meta in zip(products['documents'], products['metadatas']):
                context.append(f"Product: {meta.get('name', 'Unknown')} - {doc}")
            
            final_context = "\n".join(context) if context else ""
            
            print("\nFinal Combined Context:")
            print(final_context)
            print("\n=== RAG Debug: Context Retrieval Complete ===")
            
            return final_context
            
        except Exception as e:
            print(f"\nError getting context: {str(e)}")
            return ""

    def enhance_prompt(self, query: str, context: str) -> str:
        """
        Enhance the user query with retrieved context
        """
        enhanced_prompt = f"""Context Information:
{context}

User Query: {query}

Please provide a helpful response considering the above context. 
If the context is relevant, use it to enhance your response.
If not, you can ignore it and provide a general response.
Remember to be clear and concise in your response."""

        print("\n=== RAG Debug: Enhanced Prompt ===")
        print(enhanced_prompt)
        print("=== RAG Debug: End of Enhanced Prompt ===\n")
        
        return enhanced_prompt