# backend/utils/query_decomposer.py
import google.generativeai as genai
from typing import List, Dict
import json

class QueryDecomposer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 20,
                "max_output_tokens": 1024,
            }
        )
        
    def decompose_query(self, query: str) -> Dict[str, List[str]]:
        """Decompose main query into sub-queries and determine search necessity"""
        prompt = f"""Analyze the following health-related query and:
1. Determine if we need to search for scientific research (yes/no)
2. Decompose into 3-4 specific sub-queries if research is needed

Query: {query}

Provide response in the following JSON format:
{{
    "needs_research": true/false,
    "sub_queries": [
        "What is [topic] and its basic mechanisms?",
        "What are the proven benefits of [topic]?",
        "What are the potential risks and side effects of [topic]?",
        "What does recent scientific research say about [topic]'s safety?"
    ]
}}

If research is not needed, return empty sub_queries list.
"""

        try:
            print(f"\n=== Decomposing Query: {query} ===")
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            result = json.loads(response.text)
            print(f"Needs Research: {result['needs_research']}")
            if result['needs_research']:
                print("Sub-queries:", result['sub_queries'])
            
            return result
            
        except Exception as e:
            print(f"Error decomposing query: {str(e)}")
            return {
                "needs_research": False,
                "sub_queries": []
            }