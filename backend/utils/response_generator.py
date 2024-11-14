# backend/utils/response_generator.py
import google.generativeai as genai
from typing import Dict, List, Optional

class ResponseGenerator:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
    
    async def generate_comprehensive_response(
        self, 
        original_query: str, 
        sub_queries: List[str], 
        research_results: Dict[str, str],
        rag_context: Optional[str] = None
    ) -> str:
        """Generate comprehensive response with safety warnings"""
        
        # Prepare research summary
        research_summary = "\n\n".join([
            f"Research for '{query}':\n{results}"
            for query, results in research_results.items()
        ])
        
        prompt = f"""As a health advisor, provide a comprehensive response to the following query.
Use Chain of Thought reasoning internally but provide a clear, concise final response.

Original Query: {original_query}

{"Local Knowledge Context:" + rag_context if rag_context else ""}

Research Findings:
{research_summary}

Think through the following steps:
1. Analyze the research findings and local knowledge
2. Identify any safety concerns or warnings
3. Consider the reliability of the information
4. Formulate a balanced response

Then provide a response that:
1. Directly answers the original query
2. Includes relevant safety warnings
3. Cites research findings when available
4. Recommends consulting healthcare professionals when appropriate

Use this format:
Answer: [Clear, concise response]
Safety Warning: [If applicable]
Research Note: [Key findings from research]
Professional Advice: [When to consult healthcare providers]

Response:"""

        try:
            print("\n=== Generating Comprehensive Response ===")
            response = self.model.generate_content(prompt)
            print("Response generated successfully")
            return response.text
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return """I apologize, but I'm having trouble generating a comprehensive response. 
For your safety, please consult a healthcare professional for accurate advice."""