import os
import streamlit as st
from dotenv import load_dotenv
from helper import get_model_response, get_income_statement, get_balance_sheet, get_ticker, process_pdf

# Load environment variables
load_dotenv()

# Set Streamlit page config with black background and white text
st.set_page_config(page_title="Fundamental Analysis Dashboard", layout="wide")
st.markdown(
    """
    <style>
    .reportview-container {
        background: black;
        color: white;
    }
    .stTextArea, .stTextArea textarea {
        background-color: #333333;
        color: white;
    }
    .stDataFrame {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title of the app
st.title("Fundamental Analysis Dashboard with LLM Insights")

# Placeholder for uploaded report
st.header("Upload Annual Report")

# File uploader for the annual report
uploaded_file = st.file_uploader("Choose an annual report (PDF format)", type="pdf")

# Define the query for LLM
query = "How has the performance been in this year compared to last year?"

# Check if a file has been uploaded
if uploaded_file is not None:
    # Save the uploaded file locally
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
  
    # Process the PDF and get the database (Chroma object)
    db = process_pdf(uploaded_file.name)
    
    # Use the LLM to search for relevant context
    docs = db.similarity_search(query)
    context = docs[0].page_content
    
    # Extract company name from the uploaded file name
    company_name = uploaded_file.name.split('.')[0]
    
    # Display insights generated from LLM
    insights = get_model_response(query, context)
    st.subheader("Insights from Annual Report")
    st.text_area("Report Insights", value=insights, height=200)

    st.write(f"Analyzing the report for: {company_name}")
    
    # Get the ticker symbol for the company
    ticker = get_ticker(company_name)
    
    if ticker:
        st.write(f"Ticker Symbol: {ticker}")

        # Get income statement and balance sheet data
        st.header(f"Profit and Loss KPIs for {company_name} (Last 9 Years)")
        income_statement_df = get_income_statement(ticker)

        if income_statement_df is not None:
            st.write("All figures are in million USD")
            # Ensure all numbers have 2 decimal places and reformat table layout
            # income_statement_df[['total_rev', 'ebitda', 'net_income']] = income_statement_df[['total_rev', 'ebitda', 'net_income']].astype(float).round(0).astype(int)
            transposed_df = income_statement_df.set_index('dates').T  # Transpose to make years as columns
            st.dataframe(transposed_df)
        else:
            st.write("No income statement data available.")

        st.header(f"Balance Sheet KPIs for {company_name} (Last 9 Years)")
        balance_sheet_df = get_balance_sheet(ticker)

        if balance_sheet_df is not None:
            st.write("All figures are in millions USD")
            # Ensure all numbers have 2 decimal places and reformat table layout
            # balance_sheet_df[['debt', 'current_assets', 'cash_equivalents']] = balance_sheet_df[['debt', 'current_assets', 'cash_equivalents']].astype(float).round(0).astype(int)

            # Transpose the DataFrame to make the years as columns
            transposed_balance_sheet_df = balance_sheet_df.set_index('dates').T

            # Display the formatted DataFrame in Streamlit
            st.dataframe(transposed_balance_sheet_df)
        else:
            st.write("No balance sheet data available.")
    else:
        st.write(f"Unable to retrieve ticker symbol for {company_name}.")
    
# Note or disclaimer
st.markdown("**Note:** Data is fetched from Alphavantage API based on the uploaded PDF file name.")
