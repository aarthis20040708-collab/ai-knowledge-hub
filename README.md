# 🤖 AI Knowledge Hub & Document Assistant 🌍

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![High Speed AI Engine](https://img.shields.io/badge/AI%20Engine-LPU%20Inference-F05023?logo=fastapi&logoColor=white)](https://groq.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent, multi-tenant AI Platform and Document Assistant powered by **ultra-fast LPU inference**, **multi-document analysis**, **real-time web search grounding**, **custom user workspaces**, and **instant executive PDF report exports**.

---

## 🌟 Key Features

### ⚡ 1. Ultra-Fast Streaming Chat & Model Swapping
- Instant word-by-word token streaming for natural conversation flow.
- Dynamic dropdown to switch seamlessly between top intelligence models on the fly.

### 📁 2. Multi-File Document Q&A & Summarizer
- Upload **multiple files simultaneously** (`.pdf`, `.txt`, `.md`, `.csv`, `.py`).
- Automatic text extraction, page counting, and word counting.
- One-click **"✨ Summarize All Documents"** to synthesize insights across all uploaded files.

### 🌐 3. Real-Time Web Search & Grounding
- Live internet retrieval for up-to-date facts, current trends, and real-time knowledge.
- Bridges the gap beyond static model cutoff dates with breaking developments.

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
├── ai_engine.py            # High-speed AI client, streaming logic & model management
├── document_processor.py   # Multi-file text extraction (PyPDF & text parsers)
├── search_service.py       # Live web search grounding (DDGS)
├── pdf_generator.py        # Executive PDF report generation (ReportLab)
├── database.py             # SQLite data access layer (Users, Workspaces, Chats)
├── auth_ui.py              # Sign In and Sign Up authentication components
├── app.py                  # Standalone CLI terminal assistant
├── requirements.txt        # Production dependencies for cloud deployment
├── .gitignore              # Protects environment keys, venv, and local databases
└── README.md               # Documentation & Setup Guide
```

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | Streamlit | Responsive, interactive web dashboard |
| **AI Inference** | High-Speed LPU Engine | Real-time streaming conversational intelligence |
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

### 4. Configure Your Secure Environment
Create a `.env` file in the root directory and add your API key:
```env
GROQ_API_KEY=your_private_api_key_here
```

### 5. Run the Application
```bash
streamlit run web_app.py
```
Your browser will open automatically at `http://localhost:8501`.

---

## ☁️ Cloud Deployment

1. Push or fork this repository to your GitHub account.
2. Sign in to your cloud hosting platform (e.g., Streamlit Community Cloud).
3. Connect your repository and select `web_app.py` as the main entry point.
4. Add your private API key securely inside the platform's **Secrets / Environment Variables** settings:
   ```toml
   GROQ_API_KEY = "your_private_api_key_here"
   ```
5. Click **Deploy** to launch your app 24/7! 🚀

---

## 💻 Standalone Interactive Chatbot (CLI Version)

For quick testing directly from the terminal without launching the web server, you can run this standalone interactive chatbot script (`app.py`):

```python
import os
import sys
from dotenv import load_dotenv
from groq import Groq

# Ensure UTF-8 output on Windows terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. Load API Key
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 2. Define System Persona & Conversational Memory
messages = [
    {
        "role": "system",
        "content": "You are a friendly, helpful, and concise AI coding mentor. You answer clearly and help users learn step-by-step."
    }
]

print("=" * 60)
print("🤖 AI Knowledge Hub - Terminal Edition (Type 'quit' or 'exit' to stop)")
print("=" * 60)

# 3. Interactive Multi-Turn Loop
while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() in ["quit", "exit"]:
        print("\n👋 Goodbye! Thanks for chatting.")
        break

    if not user_input:
        continue

    # Add user message to history
    messages.append({"role": "user", "content": user_input})

    # Call AI Engine
    print("\nAI is thinking...")
    response = client.chat.completions.create(
        messages=messages,
        model="openai/gpt-oss-20b",
    )

    ai_reply = response.choices[0].message.content
    print(f"\nAI: {ai_reply}")

    # Add response to history for continuous memory
    messages.append({"role": "assistant", "content": ai_reply})
```

### To run the CLI Chatbot:
```powershell
python app.py
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/aarthis20040708-collab/ai-knowledge-hub/issues).

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
