import os
import google.generativeai as genai
from typing import Dict, List, Optional
from utils.rag_handler import RAGHandler

class GeminiHandler:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Configuration for the model
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=self.generation_config,
            system_instruction="""You are a knowledgeable health chatbot. 
            Provide clear, concise, and accurate health information. 
            When relevant context is provided, incorporate it naturally into your responses.
            Focus on being helpful and informative while maintaining a friendly tone."""
        )
        
        self.chat_sessions: Dict[str, any] = {}
        self.rag_handler = None

    def set_rag_handler(self, db_manager):
        """Set RAG handler after initialization"""
        self.rag_handler = RAGHandler(db_manager)

    def get_or_create_chat_session(self, user_id: str):
        """Get existing chat session or create new one"""
        if user_id not in self.chat_sessions:
            self.chat_sessions[user_id] = self.model.start_chat(history=[])
        return self.chat_sessions[user_id]

    async def get_response(self, user_id: str, message: str) -> str:
        try:
            print(f"\n=== Processing Message for User: {user_id} ===")
            print(f"Original Message: {message}")
            
            # Get chat session
            chat = self.get_or_create_chat_session(user_id)
            
            # Get context using RAG
            context = ""
            if self.rag_handler:
                context = self.rag_handler.get_relevant_context(message)
                message = self.rag_handler.enhance_prompt(message, context)
            
            print("\nSending enhanced prompt to Gemini...")
            
            # Get response
            response = chat.send_message(message)
            
            print("\nReceived response from Gemini:")
            print(response.text)
            print("=== Processing Complete ===\n")
            
            return response.text
            
        except Exception as e:
            print(f"Error in getting Gemini response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again."