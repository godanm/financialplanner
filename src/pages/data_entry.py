from streamlit import st
from database import get_db_session, Expense, Liability
import pandas as pd

def data_entry():
    st.title("Data Entry")

    session = get_db_session()

    st.subheader("Enter New Expense")
    with st.form(key='expense_form'):
        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        description = st.text_input("Description")
        submit_expense = st.form_submit_button("Save Expense")

        if submit_expense:
            new_expense = Expense(category=category, amount=amount, description=description)
            session.add(new_expense)
            session.commit()
            st.success("Expense saved successfully!")

    st.subheader("Enter New Liability")
    with st.form(key='liability_form'):
        liability_name = st.text_input("Liability Name")
        liability_amount = st.number_input("Liability Amount", min_value=0.0, format="%.2f")
        submit_liability = st.form_submit_button("Save Liability")

        if submit_liability:
            new_liability = Liability(name=liability_name, amount=liability_amount)
            session.add(new_liability)
            session.commit()
            st.success("Liability saved successfully!")

    st.subheader("Current Expenses")
    expenses = pd.read_sql(session.query(Expense).statement, session.bind)
    if not expenses.empty:
        st.dataframe(expenses)
    else:
        st.warning("No expenses recorded yet.")

    st.subheader("Current Liabilities")
    liabilities = pd.read_sql(session.query(Liability).statement, session.bind)
    if not liabilities.empty:
        st.dataframe(liabilities)
    else:
        st.warning("No liabilities recorded yet.")

    session.close()

if __name__ == "__main__":
    data_entry()