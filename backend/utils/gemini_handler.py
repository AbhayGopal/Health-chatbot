import os
import google.generativeai as genai
from typing import Dict, List

class GeminiHandler:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
        # Configuration for the model
        self.generation_config = {
            "temperature": 0.7,  # Lower temperature for more focused health advice
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
            For complex queries, use step-by-step reasoning internally 
            but provide only the final, simplified response."""
        )
        
        self.chat_sessions: Dict[str, any] = {}

    def get_or_create_chat_session(self, user_id: str):
        """Get existing chat session or create new one"""
        if user_id not in self.chat_sessions:
            self.chat_sessions[user_id] = self.model.start_chat(history=[])
        return self.chat_sessions[user_id]

    async def get_response(self, user_id: str, message: str, context: List[str] = None) -> str:
        try:
            # Get chat session
            chat = self.get_or_create_chat_session(user_id)
            
            # Prepare prompt with context
            prompt = message
            if context:
                prompt = f"""Context: {' '.join(context)}
                User Query: {message}
                Please provide a helpful response considering the context."""

            # Get response
            response = chat.send_message(prompt)
            
            # Extract only the final response
            final_response = self._extract_final_response(response.text)
            
            return final_response
        
        except Exception as e:
            print(f"Error in getting Gemini response: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again."

    def _extract_final_response(self, full_response: str) -> str:
        """Extract final response from CoT output"""
        # If response contains specific markers, extract only the final answer
        if "Final Answer:" in full_response:
            return full_response.split("Final Answer:")[-1].strip()
        return full_response.strip()