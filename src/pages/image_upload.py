import streamlit as st
from services.ocr_service import extract_text_from_image, parse_financial_data
import pandas as pd
from database.db_utils import get_db_session
from database.models import Asset, Expense
from datetime import datetime

def show_image_upload():

    st.title("Upload Financial Summary")

    st.markdown("""
    ### How to use:
    1. Take a screenshot or photo of your financial summary.
    2. Upload it here (PDF or image).
    3. The system will extract assets and expenses.
    4. Review and confirm the extracted data.
    """)

    uploaded_file = st.file_uploader("Choose a financial summary image", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file is not None:
        st.subheader("Uploaded Document")
        st.image(uploaded_file, caption="Your financial summary", use_column_width=True, output_format="auto", width=600, clamp=True)

        if st.button("Extract Financial Data"):
            with st.spinner("Processing your document..."):
                extracted_text = extract_text_from_image(uploaded_file)

                if extracted_text:
                    st.subheader("Extracted Text")
                    st.text_area("OCR Results", extracted_text, height=200)

                    assets, expenses = parse_financial_data(extracted_text)

                    if assets:
                        st.subheader("Extracted Assets")
                        assets_df = pd.DataFrame(assets)
                        st.dataframe(assets_df)

                        if st.button("Save Assets"):
                            session = get_db_session()
                            for _, row in assets_df.iterrows():
                                new_asset = Asset(
                                    name=row['name'],
                                    current_value=row['amount'],
                                    type="From Image"
                                )
                                session.add(new_asset)
                            session.commit()
                            session.close()
                            st.success(f"Saved {len(assets_df)} assets!")

                    if expenses:
                        st.subheader("Extracted Expenses")
                        expenses_df = pd.DataFrame(expenses)
                        st.dataframe(expenses_df)

                        if st.button("Save Expenses"):
                            session = get_db_session()
                            for _, row in expenses_df.iterrows():
                                new_expense = Expense(
                                    date=datetime.now().date(),
                                    category=row['category'],
                                    amount=row['amount'],
                                    description="From Image Upload"
                                )
                                session.add(new_expense)
                            session.commit()
                            session.close()
                            st.success(f"Saved {len(expenses_df)} expenses!")

                    if not assets and not expenses:
                        st.warning("Couldn't automatically extract financial data. Try manual entry or ask the AI advisor for help.")

if __name__ == "__main__":
    show_image_upload()