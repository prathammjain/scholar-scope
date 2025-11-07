import os
from groq import Groq
from typing import List, Dict


class LLMHandler:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"  # Updated to supported model
    
    def generate_answer(self, question: str, context_chunks: List[Dict]) -> str:
        """Generate a natural answer using retrieved context."""
        
        context = ""
        for i, chunk in enumerate(context_chunks, 1):
            context += f"\n[Source {i} - Page {chunk['page']}]\n{chunk['text']}\n"
        
        prompt = f"""You are a helpful research assistant. Answer the user's question based on the provided context from a research paper.

Context from the paper:
{context}

User Question: {question}

Instructions:
- Provide a clear, natural answer based on the context
- Cite which page/source you're referencing (e.g., "According to page 3...")
- If the context doesn't contain enough information, say so honestly
- Be concise but comprehensive
- Use a conversational, friendly tone

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant that answers questions about academic papers in a clear, natural way."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"


def get_llm_handler():
    return LLMHandler()
