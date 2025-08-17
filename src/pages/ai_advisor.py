import re

def get_ai_advice(user_question, financial_context):
    """
    Provides financial advice based on a user's question and financial data.

    This is a placeholder function. In a real application, this would
    call a large language model API (like Gemini, GPT, etc.) to generate
    the advice.

    Args:
        user_question (str): The question the user asked.
        financial_context (dict): A dictionary containing the user's financial data.

    Returns:
        str: A string containing the AI-generated advice.
    """
    print(f"User asked: {user_question}")
    print(f"Financial context provided: {financial_context}")

    # This is where you would call a Generative AI model.
    # The example below uses the financial context to provide a simple, static response.
    monthly_expenses = financial_context.get('monthly_expenses', 0)
    monthly_income = financial_context.get('monthly_income', 0)
    total_assets = financial_context.get('total_assets', 0)
    
    advice = f"""
    Based on your financial data, here is some initial advice:
    
    - Your total monthly income is ${monthly_income:.2f}.
    - Your total monthly expenses are ${monthly_expenses:.2f}.
    - Your total assets are ${total_assets:.2f}.
    
    A great first step would be to review your expenses and see if you can
    identify any areas to save. You can also explore options to grow your assets over time.
    """
    
    return advice

if __name__ == '__main__':
    # Example usage for testing purposes
    sample_context = {
        "monthly_expenses": 1500.00,
        "monthly_income": 3000.00,
        "total_assets": 50000.00,
        "total_liabilities": 10000.00,
        "family_info": [{"name": "Jane Doe", "age": 35}]
    }
    
    question = "How can I improve my financial situation?"
    advice_text = get_ai_advice(question, sample_context)
    print("\n--- AI Advice ---")
    print(advice_text)