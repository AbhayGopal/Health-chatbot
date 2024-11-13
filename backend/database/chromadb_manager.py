import chromadb
from chromadb.utils import embedding_functions
import os
from datetime import datetime
from typing import Dict, List, Optional

class ChromaDBManager:
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create collections with embedding function
        self.health_tips = self.client.get_or_create_collection(
            name="health_tips",
            embedding_function=self.embedding_function
        )
        self.products = self.client.get_or_create_collection(
            name="products",
            embedding_function=self.embedding_function
        )
        self.chat_history = self.client.get_or_create_collection(
            name="chat_history",
            embedding_function=self.embedding_function
        )
        self.feedback = self.client.get_or_create_collection(
            name="feedback",
            embedding_function=self.embedding_function
        )

        # Initialize with default data
        self._initialize_default_data()

    def _initialize_default_data(self):
        """Initialize collections with default data if empty"""
        try:
            # Initialize default health tips
            if len(self.health_tips.get()['ids']) == 0:
                default_tips = [
                    {
                        "id": "tip1",
                        "text": "Aim for 7-9 hours of sleep each night for optimal health.",
                        "category": "sleep"
                    },
                    {
                        "id": "tip2",
                        "text": "Stay hydrated by drinking at least 8 glasses of water daily.",
                        "category": "general"
                    },
                    {
                        "id": "tip3",
                        "text": "Regular exercise can improve both physical and mental health.",
                        "category": "lifestyle"
                    }
                ]
                
                for tip in default_tips:
                    self.health_tips.add(
                        documents=[tip["text"]],
                        metadatas=[{"category": tip["category"]}],
                        ids=[tip["id"]]
                    )

            # Initialize default products
            if len(self.products.get()['ids']) == 0:
                default_products = [
                    {
                        "id": "prod1",
                        "name": "Sleep Support Supplement",
                        "description": "Natural supplement with Melatonin and Magnesium for better sleep.",
                        "category": "sleep",
                        "price": 29.99
                    },
                    {
                        "id": "prod2",
                        "name": "Stress Relief Tea",
                        "description": "Herbal tea blend for relaxation and better sleep.",
                        "category": "general",
                        "price": 15.99
                    },
                    {
                        "id": "prod3",
                        "name": "Multivitamin Complex",
                        "description": "Complete daily vitamin and mineral supplement.",
                        "category": "general",
                        "price": 24.99
                    }
                ]
                
                for product in default_products:
                    self.products.add(
                        documents=[product["description"]],
                        metadatas=[{
                            "name": product["name"],
                            "category": product["category"],
                            "price": product["price"]
                        }],
                        ids=[product["id"]]
                    )
                
        except Exception as e:
            print(f"Error initializing default data: {str(e)}")

    def get_relevant_content(self, query: str, limit: int = 5) -> Dict:
        """Get relevant content based on query using vector similarity"""
        try:
            print(f"\n=== Getting Relevant Content for Query: {query} ===")
            
            # Get relevant health tips
            health_results = self.health_tips.query(
                query_texts=[query],  # Using actual query for semantic search
                n_results=min(limit, len(self.health_tips.get()['ids']))
            )
            
            # Get relevant products
            product_results = self.products.query(
                query_texts=[query],  # Using actual query for semantic search
                n_results=min(limit, len(self.products.get()['ids']))
            )
            
            print(f"Found {len(health_results['documents'][0] if health_results['documents'] else [])} relevant health tips")
            print(f"Found {len(product_results['documents'][0] if product_results['documents'] else [])} relevant products")
            
            return {
                'health_tips': {
                    'documents': health_results['documents'][0] if health_results['documents'] else [],
                    'metadatas': health_results['metadatas'][0] if health_results['metadatas'] else []
                },
                'products': {
                    'documents': product_results['documents'][0] if product_results['documents'] else [],
                    'metadatas': product_results['metadatas'][0] if product_results['metadatas'] else []
                }
            }
            
        except Exception as e:
            print(f"Error getting relevant content: {str(e)}")
            return {
                'health_tips': {'documents': [], 'metadatas': []}, 
                'products': {'documents': [], 'metadatas': []}
            }

    def get_health_tips(self, category: Optional[str] = None, limit: int = 5) -> Dict:
        """Get health tips with proper error handling"""
        try:
            if category:
                results = self.health_tips.query(
                    query_texts=["health tips"],  # Generic query for tips
                    where={"category": category},
                    n_results=min(limit, len(self.health_tips.get()['ids']))
                )
            else:
                results = self.health_tips.query(
                    query_texts=["health tips"],  # Generic query for tips
                    n_results=min(limit, len(self.health_tips.get()['ids']))
                )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else []
            }
            
        except Exception as e:
            print(f"Error getting health tips: {str(e)}")
            return {'documents': [], 'metadatas': []}

    def get_products_by_category(self, category: str) -> Dict:
        """Get products by category with proper error handling"""
        try:
            results = self.products.query(
                query_texts=[""],  # Empty query for category-based search
                where={"category": category},
                n_results=min(5, len(self.products.get()['ids']))
            )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else []
            }
            
        except Exception as e:
            print(f"Error getting products: {str(e)}")
            return {'documents': [], 'metadatas': []}

    def store_chat(self, user_id: str, message: str, response: str) -> bool:
        """Store chat with proper error handling"""
        try:
            chat_id = f"chat_{user_id}_{datetime.now().timestamp()}"
            self.chat_history.add(
                documents=[f"User: {message}\nBot: {response}"],
                metadatas=[{
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }],
                ids=[chat_id]
            )
            return True
        except Exception as e:
            print(f"Error storing chat: {str(e)}")
            return False

    def store_feedback(self, user_id: str, rating: int, comment: str) -> bool:
        """Store user feedback"""
        try:
            feedback_id = f"feedback_{user_id}_{datetime.now().timestamp()}"
            self.feedback.add(
                documents=[comment],
                metadatas=[{
                    "user_id": user_id,
                    "rating": rating,
                    "timestamp": datetime.now().isoformat()
                }],
                ids=[feedback_id]
            )
            return True
        except Exception as e:
            print(f"Error storing feedback: {str(e)}")
            return False

    def get_chat_history(self, user_id: str, limit: int = 10) -> Dict:
        """Get chat history with proper error handling"""
        try:
            results = self.chat_history.query(
                query_texts=[""],
                where={"user_id": user_id},
                n_results=min(limit, len(self.chat_history.get()['ids']))
            )
            
            return {
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else []
            }
            
        except Exception as e:
            print(f"Error getting chat history: {str(e)}")
            return {'documents': [], 'metadatas': []}