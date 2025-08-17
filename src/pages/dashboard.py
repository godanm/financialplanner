import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import get_db_session, Income, Expense, Asset, Liability

def show_dashboard():
    st.title("Financial Dashboard")
    
    session = get_db_session()
    
    total_expenses = sum(exp.amount for exp in session.query(Expense).all())
    total_income = sum(inc.amount for inc in session.query(Income).all())
    net_worth = sum(asset.current_value for asset in session.query(Asset).all()) - \
                sum(liab.amount for liab in session.query(Liability).all())
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Expenses", f"${total_expenses:,.2f}")
    col2.metric("Total Income", f"${total_income:,.2f}")
    col3.metric("Net Worth", f"${net_worth:,.2f}")
    
    st.subheader("Expense Breakdown")
    expenses = pd.read_sql(session.query(Expense).statement, session.bind)
    if not expenses.empty:
        fig, ax = plt.subplots()
        expenses.groupby('category')['amount'].sum().plot.pie(autopct='%1.1f%%', ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No expense data available.")
    
    session.close()

if __name__ == "__main__":
    show_dashboard()