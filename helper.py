from langchain import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import os
import requests
import pandas as pd


load_dotenv()

OPENAI_API_KEY=os.getenv('OPENAI_KEY')
AV_API_KEY = os.getenv('Alphavantage_key')

llm = OpenAI(openai_api_key=OPENAI_API_KEY,temperature=0, model_name="gpt-3.5-turbo-instruct", max_tokens=-1)

def process_pdf(file_path):
    """
    This function processes the uploaded PDF, splits it into text chunks, 
    and stores them in a Chroma database using OpenAI embeddings.

    Args:
        file_path (str): The path to the uploaded PDF file.
        openai_api_key (str): Your OpenAI API key for embeddings.

    Returns:
        db: The Chroma database containing the embedded documents.
    """
    # Set up OpenAI API key
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

    # Load the PDF file
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()

    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    documents = text_splitter.split_documents(pages)

    # Create a Chroma database from the documents using OpenAI embeddings
    embeddings = OpenAIEmbeddings()
    db = Chroma.from_documents(documents, embeddings)

    # Return the Chroma database
    return db


from openai import OpenAI
def get_model_response(query, context):
    load_dotenv()
    OPENAI_API_KEY = os.getenv('OPENAI_KEY')
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

    prompt = f"""
            You are a chatbot that is supposed to give response to user query's about a company's financials based on the following context.
            You are given the following context:
            {context}
            You are asked to generate a short and accurate answer to the following question using the above context.
            question: {query}
            strictly do not hallucinate. Only use the above context to generate an answer. Please give your response in bullet points.
            Remove any unwanted characters or symbols.
            """
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        max_tokens=1024,
        temperature=0,
        messages=[
            {"role": "system", "content": prompt}
        ]
    )
    
    model_response = response.choices[0].message.content
    return model_response

# query = "How has the performance been in this year compared to last year?"
# docs = db.similarity_search(query)
# print(docs[0].page_content)
# context=docs[0].page_content


def get_income_statement(symbol='INFY'):
    load_dotenv()
    
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "INCOME_STATEMENT",
        "symbol": symbol,
        "apikey": AV_API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if not data:
            print(f"No data found for {symbol}")
            return None

        rev = {'dates': [], 'total_rev': [], 'ebitda': [], 'net_income': []}
        for i in range(0, 9):
            rev['dates'].append(data['annualReports'][i]['fiscalDateEnding'])
            rev['total_rev'].append(int(data['annualReports'][i]['totalRevenue']) / 1_000_000)
            rev['ebitda'].append(int(data['annualReports'][i]['ebitda']) / 1_000_000)
            rev['net_income'].append(int(data['annualReports'][i]['netIncome']) / 1_000_000)
        
        is_df = pd.DataFrame(rev)
        is_df= is_df.sort_values(by=['dates'], ascending=True)
        is_df[['total_rev', 'ebitda', 'net_income']] = is_df[['total_rev', 'ebitda', 'net_income']].round(0).astype(int)
        return is_df
    else:
        print(f"Error fetching data: {response.status_code}")
        return None



def get_balance_sheet(symbol='INFY'):
    load_dotenv()
    
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "BALANCE_SHEET",
        "symbol": symbol,
        "apikey": AV_API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        bs_data = response.json()
        if not bs_data:
            print(f"No data found for {symbol}")
            return None

        bs = {'dates': [], 'debt': [], 'current_assets': [], 'cash_equivalents': []}
        for i in range(0, 9):
            bs['dates'].append(bs_data['annualReports'][i]['fiscalDateEnding'])
            long_term_debt = bs_data['annualReports'][i].get('longTermDebt', '0')
            bs['debt'].append(int(long_term_debt) / 1_000_000 if long_term_debt not in ['0', None, 'None', ''] else 0)
            bs['current_assets'].append(int(bs_data['annualReports'][i]['totalCurrentAssets']) / 1_000_000)
            bs['cash_equivalents'].append(int(bs_data['annualReports'][i]['cashAndCashEquivalentsAtCarryingValue']) / 1_000_000)
        
        bs_df = pd.DataFrame(bs)
        bs_df[['debt', 'current_assets', 'cash_equivalents']] = bs_df[['debt', 'current_assets', 'cash_equivalents']].round(0).astype(int)
        bs_df= bs_df.sort_values(by=['dates'], ascending=True)
        return bs_df
    else:
        print(f"Error fetching data: {response.status_code}")
        return None


company='Infosys'
def get_ticker(company):
    # Define the desired market
    desired_market = 'India/Bombay'

    # API URL to search for the company symbol
    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company}&apikey={AV_API_KEY}'
    
    # Make a GET request
    r = requests.get(url)
    
    # Parse the JSON response
    data = r.json()
    
    # Iterate over the bestMatches to find the symbol for the desired market
    for match in data.get('bestMatches', []):
        if match['4. region'] == desired_market:
            symbol = match['1. symbol'].split('.')[0]
            print(f"The symbol for {desired_market} is: {symbol}")
            return symbol
    else:
        print(f"No symbol found for the market: {desired_market}")
        return None


