<div align="center">

# 🔍 Gemini Deep Research Agent

### *Web crawling + AI writing + Citation verification — all in one click.*

[![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini_1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![Firecrawl](https://img.shields.io/badge/Firecrawl-FF6B35?style=for-the-badge&logo=firefoxbrowser&logoColor=white)](https://firecrawl.dev)

> AI-powered research tool that crawls the web, generates structured reports, verifies citations, and exports to PDF — all in one click.

</div>

---

## 📸 Demo

> *(Screenshot / GIF coming soon)*

---

## ✨ Features

- 🌐 **Live Web Crawling** — Firecrawl scrapes up to 15 URLs in real time for any topic
- 🧠 **AI Report Generation** — Gemini 1.5 Flash writes a structured, professional research report
- ✨ **Report Enhancement** — Second AI pass adds examples, statistics, and expert perspectives
- 🔬 **Citation Accuracy Engine** — Each claim is scored against crawled source material (High / Med / Low)
- 📕 **PDF Export** — Download a professional PDF with citation breakdown page
- 📄 **Markdown Export** — Download raw report as `.md` file
- ⚡ **Auto Retry** — Handles API rate limits automatically with countdown timer

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **AI Model** | Google Gemini 1.5 Flash |
| **Web Scraping** | Firecrawl Deep Research API |
| **PDF Generation** | fpdf2 |
| **Citation Engine** | Custom (SequenceMatcher + chunk scoring) |

---

## 🔬 How Citation Accuracy Works

Every sentence in the generated report is scored against the crawled source text using a **two-signal algorithm:**

- **Chunk matching** — 6-word sliding window against source content *(65% weight)*
- **Sequence similarity** — SequenceMatcher ratio against first 3000 chars *(35% weight)*

| Score | Label | Meaning |
|---|---|---|
| 70%+ | 🟢 High | Directly grounded in sources |
| 45–69% | 🟡 Med | Partially supported |
| Below 45% | 🔴 Low | May be AI-inferred |

---

## 🚀 Run Locally

### 1. Clone the repo

```bash
git clone https://github.com/Mahrang1/AI-Deep-Research-Agent.git
cd AI-Deep-Research-Agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup API keys — create a `.env` file

```env
GOOGLE_API_KEY=your_gemini_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
```

Get your free keys:
- 🔑 Gemini → [aistudio.google.com](https://aistudio.google.com)
- 🔑 Firecrawl → [firecrawl.dev](https://firecrawl.dev) *(500 free credits)*

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📦 Requirements

```txt
streamlit
google-genai
firecrawl-py
python-dotenv
fpdf2
```

---

## 📁 Project Structure

```
├── app.py              # Main Streamlit app
├── .env                # API keys (not pushed to GitHub)
├── .env.example        # Template for API keys
├── requirements.txt    # Dependencies
└── README.md
```

---

## 🙋‍♀️ Built By

**Mahrang** — [github.com/Mahrang1](https://github.com/Mahrang1)

*Powered by Google Gemini + Firecrawl | Built with Streamlit*

---

<div align="center">

*If this project helped you, drop a ⭐ — it means a lot!* 😊

</div>
