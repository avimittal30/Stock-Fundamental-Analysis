import os
import streamlit as st
from dotenv import load_dotenv
from helper import get_model_response, get_income_statement, get_balance_sheet, get_ticker, process_pdf
import matplotlib.pyplot as plt
import pandas as pd

# Load environment variables
load_dotenv()

# Set Streamlit page config with black background and colored text
st.set_page_config(page_title="Fundamental Analysis Dashboard", layout="wide")
st.markdown(
    """
    <style>
    .reportview-container, .main, .block-container {
        background-color: black;
        color: white;
    }
    .stTextArea, .stTextArea textarea {
        background-color: #333333;
        color: white;
    }
    .stDataFrame {
        color: white;
    }
    th {
        color: white;
        font-weight: bold;
    }
    td {
        color: white;
    }
    .stButton button {
        background-color: #333333;
        color: white;
    }
    h1, h2, h3, h4, h5 {
        color: #ffcc00 !important; /* Brighter color for title and subtitles */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to style the dataframe with black background and white text/borders
def style_dataframe(df, highlight_columns=None, highlight_rows=None):
    # Apply comma formatting to numeric columns
    df = df.applymap(lambda x: f"{x:,.0f}" if isinstance(x, (int, float)) else x)

    # Style DataFrame with black background, white text, and yellow borders
    styled_df = df.style.set_properties(
        **{
            'background-color': 'black',
            'color': 'white',
            'border-color': '#ffcc00',  # Yellow border (same as title color)
            'border-style': 'solid',
            'border-width': '1px'
        }
    ).set_table_styles(
        [
            {'selector': 'thead th', 'props': [('color', 'white'), ('font-weight', 'bold'), ('border-color', '#ffcc00')]},
            {'selector': 'thead', 'props': [('border-color', '#ffcc00')]},
            {'selector': 'td', 'props': [('color', 'white'), ('border-color', '#ffcc00')]},  # Yellow borders in body
        ]
    )

    # Set text within white background to black
    styled_df = styled_df.set_properties(subset=df.columns, **{'background-color': 'white', 'color': 'black'})

    # Highlight specific columns (e.g., dates) with black text
    if highlight_columns:
        styled_df = styled_df.set_properties(subset=highlight_columns, **{'color': 'black', 'background-color': 'white'})

    # Highlight specific rows (e.g., KPIs like total_rev, ebitda, net_income) with black text
    if highlight_rows:
        for row in highlight_rows:
            styled_df = styled_df.set_properties(subset=pd.IndexSlice[row, :], **{'color': 'black', 'background-color': 'white'})

    return styled_df


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
    st.text_area("Report Insights", value=insights, height=180)

    st.write(f"Analyzing the report for: {company_name}")

    # Get the ticker symbol for the company
    ticker = get_ticker(company_name)

    if ticker:
        st.write(f"Ticker Symbol: {ticker}")

        # Get income statement and balance sheet data
        st.header(f"Profit and Loss KPIs for {company_name} (Last 9 Years)")
        income_statement_df = get_income_statement(ticker)

        if income_statement_df is not None:
            st.write("All figures are in millions.")
            transposed_df = income_statement_df.set_index('dates').T  # Transpose to make years as columns

            # Create columns for layout
            col1, col2 = st.columns([2, 1])

            # Display income statement table in the left column with styled DataFrame
            with col1:
                st.dataframe(style_dataframe(transposed_df))

            # Extract year from dates for graph
            income_statement_df['dates'] = pd.to_datetime(income_statement_df['dates'])
            income_statement_df['year'] = income_statement_df['dates'].dt.year

            # Display net_income graph in the right column
            with col2:
                fig, ax = plt.subplots()
                fig.patch.set_facecolor('black')
                ax.set_facecolor('black')
                ax.plot(income_statement_df['year'], income_statement_df['net_income'], color='cyan', marker='o')
                ax.set_title('Net Income Over Years', color='#ffcc00')  # Brighter color for the graph title
                ax.set_ylabel('Net Income (millions)', color='white')
                ax.set_xlabel('Year', color='white')
                ax.tick_params(colors='white')
                st.pyplot(fig)
        else:
            st.write("No income statement data available.")

        st.header(f"Balance Sheet KPIs for {company_name} (Last 9 Years)")
        balance_sheet_df = get_balance_sheet(ticker)

        if balance_sheet_df is not None:
            st.write("All figures are in millions.")
            transposed_balance_sheet_df = balance_sheet_df.set_index('dates').T

            # Create columns for layout
            col1, col2 = st.columns([2, 1])

            # Display balance sheet table in the left column with styled DataFrame
            with col1:
                st.dataframe(style_dataframe(transposed_balance_sheet_df))

            # Extract year from dates for graph
            balance_sheet_df['dates'] = pd.to_datetime(balance_sheet_df['dates'])
            balance_sheet_df['year'] = balance_sheet_df['dates'].dt.year

            # Display current_assets graph in the right column
            with col2:
                fig, ax = plt.subplots()
                fig.patch.set_facecolor('black')
                ax.set_facecolor('black')
                ax.plot(balance_sheet_df['year'], balance_sheet_df['current_assets'], color='green', marker='o')
                ax.set_title('Current Assets Over Years', color='#ffcc00')  # Brighter color for the graph title
                ax.set_ylabel('Current Assets (millions)', color='white')
                ax.set_xlabel('Year', color='white')
                ax.tick_params(colors='white')
                st.pyplot(fig)
        else:
            st.write("No balance sheet data available.")
    else:
        st.write(f"Unable to retrieve ticker symbol for {company_name}.")

# Note or disclaimer
st.markdown("**Note:** Data is fetched from Alphavantage API based on the uploaded PDF file name.")
