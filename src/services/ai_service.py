from typing import List, Dict
import ollama

class AIService:
    def __init__(self, model_name: str = 'mistral'):
        self.model_name = model_name

    def get_advice(self, context: str, user_question: str) -> str:
        messages = [
            {
                'role': 'system',
                'content': f"You are a financial advisor. Use this context to answer questions:\n{context}\nProvide specific, actionable advice based on the user's financial situation."
            },
            {
                'role': 'user',
                'content': user_question
            }
        ]
        
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Error connecting to AI model: {e}") from e

    def analyze_financial_data(self, financial_data: Dict) -> str:
        context = f"""
        Financial Overview:
        - Monthly Expenses: ${financial_data.get('total_expenses', 0):,.2f}
        - Monthly Income: ${financial_data.get('total_income', 0):,.2f}
        - Assets: ${financial_data.get('total_assets', 0):,.2f}
        - Liabilities: ${financial_data.get('total_liabilities', 0):,.2f}
        """
        return context