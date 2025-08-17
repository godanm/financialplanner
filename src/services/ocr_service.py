import re

def extract_text_from_image(uploaded_file):
    """
    Simulates extracting text from an image.
    
    This function acts as a placeholder for actual OCR logic.
    For this example, it returns a hardcoded string.
    
    Args:
        uploaded_file: The file data to be processed.
        
    Returns:
        A string containing the extracted text.
    """
    print("Simulating OCR to extract text from image...")
    # This is a placeholder. You can replace this function with your
    # pytesseract-based implementation once the import error is resolved.
    
    sample_text = """
    Financial Statement - May 2025
    
    Income:
    Salary: $5000.00
    Freelance Work: $1200.50
    Total Income: $6200.50
    
    Expenses:
    Rent: $1500.00
    Groceries: $450.75
    Utilities: $210.00
    Internet: $75.00
    Car Payment: $350.00
    Total Expenses: $2585.75
    
    Net Savings: $3614.75
    """
    return sample_text

def parse_financial_data(text):
    """
    Parses financial data (income, expenses) from a block of text.
    
    This function uses regular expressions to find dollar amounts and
    associated labels from the text provided by the OCR function.
    
    Args:
        text: The string containing financial text.
        
    Returns:
        A tuple containing two lists of dictionaries:
        - The first list contains asset/income data.
        - The second list contains expense data.
    """
    print("Parsing financial data from text...")
    
    assets = []
    expenses = []
    
    # Regex to find a label and a dollar amount
    pattern = re.compile(r"(\w[\w\s]*):\s*\$(\d+\.\d{2})")
    
    lines = text.split('\n')
    current_section = None
    
    for line in lines:
        if "Income:" in line:
            current_section = "income"
            continue
        if "Expenses:" in line:
            current_section = "expenses"
            continue
            
        match = pattern.search(line)
        if match:
            label = match.group(1).strip()
            amount = float(match.group(2))
            
            if current_section == "income":
                assets.append({"name": label, "amount": amount})
            elif current_section == "expenses":
                expenses.append({"category": label, "amount": amount})
    
    # Returning two separate lists to match the Streamlit code's unpacking
    return (assets, expenses)

# Example of how to use the functions within the same file for testing
if __name__ == "__main__":
    # In a real app, you would pass an actual image here
    dummy_image = "not a real image" 
    
    # Step 1: Extract text from the image
    extracted_text = extract_text_from_image(dummy_image)
    print("\n--- Extracted Text ---\n", extracted_text)
    
    # Step 2: Parse the financial data from the text
    # It now returns two lists of dictionaries
    parsed_income, parsed_expenses = parse_financial_data(extracted_text)
    print("\n--- Parsed Income Data ---")
    print(parsed_income)
    print("\n--- Parsed Expense Data ---")
    print(parsed_expenses)
