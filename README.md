# fundamental_analysis

Demo available on:
https://huggingface.co/spaces/avimittal30/fundamental_analysis

# 📊 Fundamental Analysis Dashboard with LLM Insights

This is an interactive **Streamlit** dashboard that performs **fundamental financial analysis** on company annual reports. It leverages the power of **Large Language Models (LLMs)** to provide intelligent summaries from PDF reports and combines that with historical financial data for a holistic view of company performance.

---

## 🚀 Features

- 📎 **Upload Annual Reports**: Upload a company’s annual report in PDF format.
- 🧠 **LLM Insights**: Get a summarized performance overview using a language model (e.g., OpenAI GPT).
- 💹 **Financial KPIs**: Visualize key financial metrics from the **Profit & Loss** and **Balance Sheet** statements.
- 🔍 **Auto Ticker Detection**: Automatically extracts the company name from the PDF and retrieves the ticker symbol.
- 📈 **Historical Trends**: Plots of Net Income and Current Assets over the last 9 years.
- 🌙 **Dark Themed UI**: A clean black background with styled tables and bright visuals.

---

## 🧰 Tech Stack

- **Frontend/UI**: Streamlit
- **Language Model**: OpenAI GPT via LangChain
- **Vector Store**: ChromaDB
- **PDF Parsing**: `PyMuPDF` or `pdfminer.six` (depending on `process_pdf` implementation)
- **Financial Data**: Alphavantage API
- **Visualization**: Matplotlib
- **Env Management**: Python-dotenv

---

## 📦 Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/fundamental-analysis-dashboard.git
   cd fundamental-analysis-dashboard


Please view the demo on 




