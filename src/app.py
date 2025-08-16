import streamlit as st
from database import init_db, get_db_session
from pages import dashboard, data_entry, image_upload, ai_advisor

def main():
    # Initialize the database
    init_db()

    # Set up the Streamlit page configuration
    st.set_page_config(page_title="Financial Analysis App", layout="wide")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Data Entry", "Image Upload", "AI Advisor"])

    # Route to the selected page
    if page == "Dashboard":
        dashboard.show_dashboard()
    elif page == "Data Entry":
        data_entry.show_data_entry()
    elif page == "Image Upload":
        image_upload.show_image_upload()
    elif page == "AI Advisor":
        ai_advisor.show_ai_advisor()

if __name__ == "__main__":
    main()