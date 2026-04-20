# 🔍 Gemini Deep Research Agent

> AI-powered research tool that crawls the web, generates structured reports, verifies citations, and exports to PDF — all in one click.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=flat&logo=google&logoColor=white)
![Firecrawl](https://img.shields.io/badge/Firecrawl-orange?style=flat)

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
| Frontend | Streamlit |
| AI Model | Google Gemini 1.5 Flash |
| Web Scraping | Firecrawl Deep Research API |
| PDF Generation | fpdf2 |
| Citation Engine | Custom (SequenceMatcher + chunk scoring) |

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/Mahrang1/deep-research-agent.git
cd deep-research-agent
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Setup API keys — create a `.env` file:**
```
GOOGLE_API_KEY=your_gemini_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
```

Get your free keys:
- 🔑 Gemini → [aistudio.google.com](https://aistudio.google.com)
- 🔑 Firecrawl → [firecrawl.dev](https://firecrawl.dev) (500 free credits)

**4. Run the app**
```bash
streamlit run app.py
```

---

## 📦 Requirements

```
streamlit
google-genai
firecrawl-py
python-dotenv
fpdf2
```

---

## 🔬 How Citation Accuracy Works

Every sentence in the generated report is scored against the crawled source text using a two-signal algorithm:

- **Chunk matching** — 6-word sliding window against source content (65% weight)
- **Sequence similarity** — SequenceMatcher ratio against first 3000 chars (35% weight)

Scores are shown per-claim and as an overall percentage:

| Score | Label | Meaning |
|---|---|---|
| 70%+ | 🟢 High | Directly grounded in sources |
| 45–69% | 🟡 Medium | Partially supported |
| Below 45% | 🔴 Low | May be AI-inferred |

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

---

<p align="center">Powered by Google Gemini + Firecrawl | Built with Streamlit</p>
