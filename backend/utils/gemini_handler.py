# backend/utils/gemini_handler.py
import google.generativeai as genai
from typing import Dict, List, Optional
from utils.rag_handler import RAGHandler
from utils.query_decomposer import QueryDecomposer
from utils.search_controller import SearchController
from utils.response_generator import ResponseGenerator
from config import Config

class GeminiHandler:
    def __init__(self, config: Config):
        self.config = config
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        # Initialize components
        self.query_decomposer = QueryDecomposer(config.GOOGLE_API_KEY)
        self.search_controller = SearchController(config.SONAR_API_KEY)
        self.response_generator = ResponseGenerator(config.GOOGLE_API_KEY)
        self.rag_handler = None
        
        # Initialize chat sessions
        self.chat_sessions: Dict[str, any] = {}

    def set_rag_handler(self, db_manager):
        """Set RAG handler after initialization"""
        self.rag_handler = RAGHandler(db_manager)

    async def get_response(self, user_id: str, message: str) -> str:
        """Process user message and generate response"""
        try:
            print(f"\n=== Processing Message for User: {user_id} ===")
            print(f"Original Message: {message}")
            
            # Step 1: Decompose query and check if research needed
            decomposition_result = self.query_decomposer.decompose_query(message)
            needs_research = decomposition_result['needs_research']
            sub_queries = decomposition_result['sub_queries']
            
            # Step 2: Get research results if needed
            research_results = {}
            if needs_research and sub_queries:
                print("\n=== Conducting Research ===")
                research_results = await self.search_controller.search_research(sub_queries)
            
            # Step 3: Get RAG context
            rag_context = ""
            if self.rag_handler:
                print("\n=== Getting RAG Context ===")
                rag_context = self.rag_handler.get_relevant_context(message)
            
            # Step 4: Generate comprehensive response
            print("\n=== Generating Response ===")
            response = await self.response_generator.generate_comprehensive_response(
                original_query=message,
                sub_queries=sub_queries,
                research_results=research_results,
                rag_context=rag_context
            )
            
            # Store chat history
            self._update_chat_history(user_id, message, response)
            
            print("\n=== Response Generation Complete ===")
            return response
            
        except Exception as e:
            print(f"Error in getting response: {str(e)}")
            return self.config.DEFAULT_RESPONSE

    def _update_chat_history(self, user_id: str, message: str, response: str):
        """Update chat history for user"""
        if user_id not in self.chat_sessions:
            self.chat_sessions[user_id] = []
        
        self.chat_sessions[user_id].append({
            "role": "user",
            "content": message
        })
        self.chat_sessions[user_id].append({
            "role": "assistant",
            "content": response
        })
        
        # Keep only recent history
        if len(self.chat_sessions[user_id]) > self.config.MAX_CHAT_HISTORY * 2:
            self.chat_sessions[user_id] = self.chat_sessions[user_id][-self.config.MAX_CHAT_HISTORY * 2:]