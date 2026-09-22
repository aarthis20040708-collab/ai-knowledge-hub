# 🤖 AI Knowledge Hub & Document Assistant 🌍

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Groq LPU](https://img.shields.io/badge/Groq-LPU%20Inference-F05023?logo=fastapi&logoColor=white)](https://groq.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent, multi-tenant AI Platform and Document Assistant powered by **Groq ultra-fast LPU inference**, **multi-document analysis**, **real-time web search grounding**, **custom user workspaces**, and **instant executive PDF report exports**.

---

## 🌟 Key Features

### ⚡ 1. Ultra-Fast Streaming Chat & Model Swapping
- Instant word-by-word token streaming powered by Groq's high-speed inference engine.
- Dynamic dropdown to switch on the fly between cutting-edge open-weight models (`openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, and more).

### 📁 2. Multi-File Document Q&A & Summarizer
- Upload **multiple files simultaneously** (`.pdf`, `.txt`, `.md`, `.csv`, `.py`).
- Automatic text extraction, page counting, and word counting.
- One-click **"✨ Summarize All Documents"** to synthesize insights across all uploaded files.

### 🌐 3. Real-Time Web Search & Grounding
- Live internet retrieval powered by `ddgs` (DuckDuckGo).
- Bridges the gap beyond static model cutoff dates with breaking news and real-time facts.

### ⏳ 4. Past, Present & Future Predictive Intelligence
- Multi-dimensional temporal reasoning: historical foundations (**Past**), current state-of-the-art reality (**Present**), and forward-looking strategic projections (**Future**).
- Specialized personas for **Societal Impact & Sustainability**, **Future Forecasting**, and **Tech-for-Good**.

### 📄 5. Instant Executive PDF Report Generator
- 1-click **"📥 Download as PDF"** on every response without outputting raw code.
- Full session export via **"📥 Export PDF"** in the top navigation.
- Crash-proof, formatted with headers, timestamps, metadata, clean typography, and bullet points via ReportLab.

### 🔐 6. User Authentication & Custom Workspaces
- User registration and login with secure **SHA-256 password hashing**.
- Multi-workspace organization (e.g. *Research Hub*, *Coding Projects*, *Social Impact Initiatives*).

### 🔍 7. Searchable Chat History
- Persistent chat storage powered by SQLite (`app_data.db`).
- Real-time keyword search bar across all conversation titles and message history.
- Easy thread management: create new chats (`➕`), switch threads, or delete (`🗑️`).

---

## 🏗️ Architecture & Tech Stack

```
ai-knowledge-hub/
│
├── web_app.py              # Main Streamlit web application & chat UI
├── ai_engine.py            # Groq client, streaming logic, and model management
├── document_processor.py   # Multi-file text extraction (PyPDF & text parsers)
├── search_service.py       # Live web search grounding (DDGS)
├── pdf_generator.py        # Executive PDF report generation (ReportLab)
├── database.py             # SQLite data access layer (Users, Workspaces, Chats)
├── auth_ui.py              # Sign In and Sign Up authentication components
├── app.py                  # Lightweight CLI terminal assistant
├── requirements.txt        # Production dependencies for cloud deployment
├── .gitignore              # Protects .env, venv, and local databases
└── README.md               # Documentation & Setup Guide
```

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit | Responsive, interactive web dashboard |
| **LLM Engine** | Groq SDK | Lightning-fast inference on open LLMs |
| **Document Parsing** | PyPDF / BytesIO | PDF & text multi-file extraction |
| **Web Grounding** | DDGS | Real-time live web facts & citations |
| **Report Generation** | ReportLab | Formatted executive PDF document generation |
| **Storage & Auth** | SQLite3 / hashlib | User credentials, workspaces, message history |

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the Repository
```bash
git clone https://github.com/aarthis20040708-collab/ai-knowledge-hub.git
cd ai-knowledge-hub
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```
> Get your free API key at [Groq Console](https://console.groq.com/).

### 5. Run the Application
```bash
streamlit run web_app.py
```
Your browser will open automatically at `http://localhost:8501`.

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Fork or push this repository to your GitHub account.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app** and select your repository: `ai-knowledge-hub`.
4. Set Main file path to: `web_app.py`.
5. Under **Advanced settings** > **Secrets**, add your Groq key:
   ```toml
   GROQ_API_KEY = "gsk_your_actual_groq_key_here"
   ```
6. Click **Deploy!** 🚀

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/aarthis20040708-collab/ai-knowledge-hub/issues).

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
