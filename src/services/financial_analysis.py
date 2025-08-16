from database import get_db_session, Expense, Income, Asset, Liability

def calculate_total_expenses():
    session = get_db_session()
    total_expenses = sum(exp.amount for exp in session.query(Expense).all())
    session.close()
    return total_expenses

def calculate_total_income():
    session = get_db_session()
    total_income = sum(inc.amount for inc in session.query(Income).all())
    session.close()
    return total_income

def calculate_net_worth():
    session = get_db_session()
    total_assets = sum(asset.current_value for asset in session.query(Asset).all())
    total_liabilities = sum(liab.amount for liab in session.query(Liability).all())
    session.close()
    return total_assets - total_liabilities

def generate_financial_summary():
    total_expenses = calculate_total_expenses()
    total_income = calculate_total_income()
    net_worth = calculate_net_worth()
    
    summary = {
        "Total Expenses": total_expenses,
        "Total Income": total_income,
        "Net Worth": net_worth
    }
    
    return summary