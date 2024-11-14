# backend/utils/search_controller.py
from openai import AsyncOpenAI
from typing import List, Dict
import json
import asyncio

class SearchController:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "llama-3.1-sonar-small-128k-online"
    
    async def search_research(self, queries: List[str]) -> Dict[str, str]:
        """Search for research papers and medical data"""
        results = {}
        
        # Process queries concurrently
        async def process_query(query: str) -> tuple:
            try:
                print(f"\n=== Searching for: {query} ===")
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": """You are a medical research assistant. Search and summarize recent, reliable research papers and medical data.
Focus on:
1. Scientific evidence and clinical studies
2. Potential health risks and safety concerns
3. Expert medical opinions
4. Recent research findings

Format your response to include:
- Key findings
- Safety warnings
- Scientific consensus
- References to studies (if available)"""
                        },
                        {
                            "role": "user",
                            "content": f"Search for recent scientific research about: {query}"
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1024
                )
                
                content = response.choices[0].message.content
                print(f"Found research for: {query}")
                return query, content
                
            except Exception as e:
                print(f"Error searching for {query}: {str(e)}")
                return query, f"Error retrieving research: {str(e)}"
        
        # Process all queries concurrently
        tasks = [process_query(query) for query in queries]
        query_results = await asyncio.gather(*tasks)
        
        # Convert results to dictionary
        results = dict(query_results)
        
        return results