def format_currency(amount):
    """Format a number as currency."""
    return f"${amount:,.2f}"

def validate_positive_number(value):
    """Check if the provided value is a positive number."""
    if value < 0:
        raise ValueError("Value must be a positive number.")
    return True

def parse_date(date_string):
    """Parse a date string into a datetime object."""
    from datetime import datetime
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")

def calculate_percentage(part, whole):
    """Calculate the percentage of a part relative to a whole."""
    if whole == 0:
        return 0
    return (part / whole) * 100

def summarize_financial_data(expenses, income):
    """Generate a summary of financial data."""
    total_expenses = sum(expenses)
    total_income = sum(income)
    net_worth = total_income - total_expenses
    return {
        "total_expenses": total_expenses,
        "total_income": total_income,
        "net_worth": net_worth,
        "expense_percentage": calculate_percentage(total_expenses, total_income)
    }