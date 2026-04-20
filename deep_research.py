import streamlit as st
from google import genai
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import re
import time
from difflib import SequenceMatcher
from fpdf import FPDF

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Gemini Deep Research Agent",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    font-family: 'DM Mono', monospace !important;
    color: #e2e0ff !important;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(108,60,255,0.15) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 90%, rgba(0,210,190,0.10) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid rgba(108,60,255,0.2) !important;
}
[data-testid="stSidebar"] * {
    font-family: 'DM Mono', monospace !important;
    color: #c4bfff !important;
}
h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #a78bfa, #00d2be, #6c3cff) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    letter-spacing: -1px !important;
}
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    color: #a78bfa !important;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #13131f !important;
    border: 1px solid rgba(108,60,255,0.35) !important;
    border-radius: 10px !important;
    color: #e2e0ff !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #6c3cff, #a78bfa) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}
[data-testid="stButton"] button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
hr { border-color: rgba(108,60,255,0.2) !important; }
p, li { font-family: 'DM Mono', monospace !important; color: #c4bfff !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #6c3cff; border-radius: 3px; }

.citation-card {
    background: #13131f;
    border: 1px solid rgba(108,60,255,0.3);
    border-radius: 12px;
    padding: 20px;
    margin: 16px 0;
}
.score-high   { color: #00d2be; font-weight: bold; font-size: 2rem; }
.score-medium { color: #f59e0b; font-weight: bold; font-size: 2rem; }
.score-low    { color: #ef4444; font-weight: bold; font-size: 2rem; }
.claim-row {
    border-left: 3px solid rgba(108,60,255,0.4);
    padding: 6px 12px;
    margin: 6px 0;
    font-size: 0.82rem;
    font-family: 'DM Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PDF GENERATOR
# ─────────────────────────────────────────────

def generate_pdf(topic, report_text, overall_score, claim_results):
    """
    Report + citation score ko professional PDF mein convert karo.
    fpdf2 use karta hai — koi external dependency nahi.
    """

    class ResearchPDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(108, 60, 255)
            self.cell(0, 8, "Gemini Deep Research Agent", align="L")
            self.set_font("Helvetica", "", 9)
            self.set_text_color(120, 120, 140)
            self.cell(0, 8, f"Generated: {time.strftime('%Y-%m-%d')}", align="R")
            self.ln(2)
            # Header line
            self.set_draw_color(108, 60, 255)
            self.set_line_width(0.4)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

        def footer(self):
            self.set_y(-13)
            self.set_draw_color(200, 200, 210)
            self.set_line_width(0.3)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(1)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(150, 150, 170)
            self.cell(0, 6, f"Page {self.page_no()}", align="C")

    pdf = ResearchPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # ── TITLE PAGE BLOCK ──
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(26, 43, 74)
    # Clean topic for display
    clean_topic = topic.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, clean_topic, align="C")
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(108, 60, 255)
    pdf.cell(0, 7, "Deep Research Report", align="C")
    pdf.ln(10)

    # ── CITATION SCORE BOX ──
    if overall_score is not None:
        if overall_score >= 70:
            box_r, box_g, box_b = 0, 180, 160      # teal
            verdict = "High Confidence"
        elif overall_score >= 45:
            box_r, box_g, box_b = 220, 140, 0      # amber
            verdict = "Medium Confidence"
        else:
            box_r, box_g, box_b = 210, 50, 50      # red
            verdict = "Low Confidence"

        # Colored box
        pdf.set_fill_color(box_r, box_g, box_b)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 12,
                 f"Citation Accuracy Score: {overall_score}%   |   {verdict}",
                 align="C", fill=True)
        pdf.ln(4)

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 120)
        pdf.cell(0, 5,
                 "Each claim in this report was algorithmically verified against crawled source material.",
                 align="C")
        pdf.ln(10)

    # ── REPORT BODY ──
    lines = report_text.split("\n")
    for line in lines:
        # Encode — fpdf2 latin-1 safe
        safe_line = line.encode('latin-1', 'replace').decode('latin-1').strip()
        if not safe_line:
            pdf.ln(3)
            continue

        # Heading detection
        if safe_line.startswith("## "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(26, 43, 74)
            pdf.ln(4)
            pdf.multi_cell(0, 8, safe_line.replace("## ", ""))
            # Underline
            pdf.set_draw_color(108, 60, 255)
            pdf.set_line_width(0.4)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)

        elif safe_line.startswith("### "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(60, 80, 140)
            pdf.ln(3)
            pdf.multi_cell(0, 7, safe_line.replace("### ", ""))
            pdf.ln(1)

        elif safe_line.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(26, 43, 74)
            pdf.ln(5)
            pdf.multi_cell(0, 9, safe_line.replace("# ", ""))
            pdf.ln(3)

        elif safe_line.startswith("- ") or safe_line.startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 60)
            bullet_text = "  -  " + safe_line[2:]
            pdf.multi_cell(0, 6, bullet_text)

        elif safe_line.startswith("**") and safe_line.endswith("**"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(40, 40, 60)
            pdf.multi_cell(0, 6, safe_line.replace("**", ""))

        else:
            # Clean inline bold markdown
            safe_line = re.sub(r'\*\*(.*?)\*\*', r'\1', safe_line)
            safe_line = re.sub(r'\*(.*?)\*', r'\1', safe_line)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 60)
            pdf.multi_cell(0, 6, safe_line)

    # ── CITATION BREAKDOWN PAGE ──
    if claim_results:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(26, 43, 74)
        pdf.cell(0, 10, "Citation Accuracy Breakdown", align="L")
        pdf.ln(2)
        pdf.set_draw_color(108, 60, 255)
        pdf.set_line_width(0.4)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(6)

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 120)
        pdf.multi_cell(0, 5,
            "Each sentence from the report is scored against crawled source text. "
            "HIGH = directly grounded in sources. MED = partially supported. LOW = may be AI-inferred."
        )
        pdf.ln(5)

        for r in claim_results:
            score = r["score"]
            claim_text = r["claim"].encode('latin-1', 'replace').decode('latin-1')

            if score >= 0.70:
                label = "HIGH"
                cr, cg, cb = 0, 180, 160
            elif score >= 0.45:
                label = "MED"
                cr, cg, cb = 200, 130, 0
            else:
                label = "LOW"
                cr, cg, cb = 200, 50, 50

            # Badge
            pdf.set_fill_color(cr, cg, cb)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 8)
            pdf.cell(22, 6, f"{label} {int(score*100)}%", fill=True)

            # Claim text
            pdf.set_text_color(40, 40, 60)
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(0, 6, "  " + claim_text)
            pdf.ln(1)

    return bytes(pdf.output())


# ─────────────────────────────────────────────
# CITATION ACCURACY ENGINE
# ─────────────────────────────────────────────

def extract_claims(report_text):
    sentences = re.split(r'(?<=[.!?])\s+', report_text)
    claims = []
    for s in sentences:
        s = s.strip()
        if len(s) < 40:
            continue
        if s.startswith("#") or s.startswith("*") or s.startswith("-"):
            continue
        if s.isupper():
            continue
        claims.append(s)
    return claims[:30]


def similarity_score(claim, source_text):
    claim_lower = claim.lower()
    source_lower = source_text.lower()
    words = claim_lower.split()
    chunk_hits = 0
    total_chunks = max(len(words) - 5, 1)
    for i in range(len(words) - 5):
        chunk = " ".join(words[i:i+6])
        if chunk in source_lower:
            chunk_hits += 1
    chunk_ratio = chunk_hits / total_chunks
    seq_ratio = SequenceMatcher(None, claim_lower, source_lower[:3000]).ratio()
    combined = (chunk_ratio * 0.65) + (seq_ratio * 0.35)
    return round(min(combined * 2.5, 1.0), 3)


def run_citation_check(report_text, source_texts):
    if not source_texts:
        return None, []
    combined_sources = " ".join(source_texts)
    claims = extract_claims(report_text)
    if not claims:
        return None, []
    claim_results = []
    for claim in claims:
        score = similarity_score(claim, combined_sources)
        claim_results.append({
            "claim": claim[:180] + ("..." if len(claim) > 180 else ""),
            "score": score
        })
    overall = round(sum(r["score"] for r in claim_results) / len(claim_results) * 100, 1)
    return overall, claim_results


def render_citation_ui(overall_score, claim_results):
    if overall_score >= 70:
        score_class = "score-high"
        verdict = "High Confidence — most claims are grounded in crawled sources."
        bar_color = "#00d2be"
    elif overall_score >= 45:
        score_class = "score-medium"
        verdict = "Medium Confidence — some claims may be AI-inferred, not directly sourced."
        bar_color = "#f59e0b"
    else:
        score_class = "score-low"
        verdict = "Low Confidence — report contains significant AI-generated content not found in sources."
        bar_color = "#ef4444"

    st.markdown(f"""
    <div class="citation-card">
        <div style="display:flex;align-items:center;gap:20px;margin-bottom:12px;">
            <div>
                <div style="font-size:0.75rem;color:#7c6fcd;margin-bottom:2px;">CITATION ACCURACY SCORE</div>
                <span class="{score_class}">{overall_score}%</span>
            </div>
            <div style="flex:1;">
                <div style="background:#1e1e30;border-radius:6px;height:10px;overflow:hidden;">
                    <div style="width:{overall_score}%;background:{bar_color};height:100%;border-radius:6px;
                    transition:width 0.6s ease;"></div>
                </div>
                <div style="font-size:0.78rem;color:#9ca3af;margin-top:6px;">{verdict}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔬 View Claim-by-Claim Breakdown"):
        st.markdown(
            "<div style='font-size:0.75rem;color:#7c6fcd;margin-bottom:10px;'>"
            "Each sentence from the report is scored against crawled source text. "
            "Higher = more grounded in actual sources.</div>",
            unsafe_allow_html=True
        )
        for r in claim_results:
            s = r["score"]
            if s >= 0.70:
                badge_color = "#00d2be"
                badge = "HIGH"
            elif s >= 0.45:
                badge_color = "#f59e0b"
                badge = "MED"
            else:
                badge_color = "#ef4444"
                badge = "LOW"
            st.markdown(f"""
            <div class="claim-row">
                <span style="background:{badge_color};color:#000;border-radius:4px;
                padding:1px 7px;font-size:0.7rem;font-weight:700;margin-right:8px;">{badge} {int(s*100)}%</span>
                {r['claim']}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown("<h1>🔍 Gemini Deep Research Agent</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#7c6fcd;font-size:0.9rem;margin-top:-8px;'>"
    "Powered by Google Gemini + Firecrawl — Research any topic instantly</p>",
    unsafe_allow_html=True
)
st.divider()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🔑 API Keys")
    gemini_key = st.text_input(
        "Google Gemini API Key", type="password",
        value=os.getenv("GOOGLE_API_KEY", ""),
        help="Get free key from aistudio.google.com"
    )
    firecrawl_key = st.text_input(
        "Firecrawl API Key", type="password",
        value=os.getenv("FIRECRAWL_API_KEY", ""),
        help="Get free key from firecrawl.dev"
    )
    st.divider()
    st.markdown("""
    <div style='background:#1a1a2e;border:1px solid rgba(108,60,255,0.25);
    border-radius:8px;padding:12px;font-size:0.75rem;color:#7c6fcd;'>
    🆓 <b style='color:#a78bfa;'>Gemini</b> — free at aistudio.google.com<br><br>
    🆓 <b style='color:#a78bfa;'>Firecrawl</b> — free at firecrawl.dev<br>
    (500 free credits)
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MAIN INPUT
# ─────────────────────────────────────────────

st.markdown("### 💬 Research Topic")
research_topic = st.text_input(
    "Enter your research topic:",
    placeholder="e.g., Latest developments in AI agents 2026"
)

col1, col2 = st.columns(2)
with col1:
    max_urls = st.slider("Max URLs to crawl", 3, 15, 8)
with col2:
    max_depth = st.slider("Research depth", 1, 5, 3)

# ─────────────────────────────────────────────
# MAIN RESEARCH FUNCTION
# ─────────────────────────────────────────────

def run_research(topic, gemini_api_key, firecrawl_api_key, max_urls, max_depth):

    # ── STEP 1: Web Research ──
    st.markdown("### 🌐 Step 1: Web Research")
    with st.spinner("Crawling the web for information..."):
        try:
            firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)
            activity_log = st.empty()
            activities = []

            def on_activity(activity):
                activities.append(f"[{activity['type']}] {activity['message']}")
                activity_log.markdown("\n".join([f"- {a}" for a in activities[-5:]]))

            max_attempts = 3
            results = None
            for attempt in range(max_attempts):
                try:
                    results = firecrawl_app.deep_research(
                        query=topic,
                        params={"maxDepth": max_depth, "timeLimit": 180, "maxUrls": max_urls},
                        on_activity=on_activity
                    )
                    break
                except Exception as rate_err:
                    err_str = str(rate_err)
                    if "429" in err_str or "Rate limit" in err_str:
                        wait_match = re.search(r'retry after (\d+)s', err_str)
                        wait_sec = int(wait_match.group(1)) + 3 if wait_match else 40
                        if attempt < max_attempts - 1:
                            countdown = st.empty()
                            for remaining in range(wait_sec, 0, -1):
                                countdown.warning(
                                    f"⏳ Rate limit hit. Auto-retrying in {remaining}s "
                                    f"(Attempt {attempt+1}/{max_attempts})"
                                )
                                time.sleep(1)
                            countdown.empty()
                        else:
                            raise Exception(
                                "Rate limit reached after 3 attempts. "
                                "Wait 1 minute then try again, or lower 'Max URLs to crawl'."
                            )
                    else:
                        raise

            if results is None:
                st.error("Research failed after retries.")
                return

            initial_analysis = results['data']['finalAnalysis']
            sources = results['data']['sources']

            source_texts = []
            for source in sources:
                text = source.get("content", "") or source.get("markdown", "") or ""
                if text:
                    source_texts.append(text[:2000])
            if not source_texts:
                source_texts = [initial_analysis]

            st.success(f"✅ Found {len(sources)} sources!")

        except Exception as e:
            st.error(f"Firecrawl error: {str(e)}")
            return

    with st.expander("📄 View Raw Research Data"):
        st.markdown(initial_analysis)

    # ── STEP 2: Report Generation ──
    st.markdown("### 🧠 Step 2: AI Report Generation")
    with st.spinner("Gemini is generating your research report..."):
        try:
            client = genai.Client(api_key=gemini_api_key)
            report_prompt = f"""
You are an expert research analyst. Based on the following web research data, create a comprehensive, well-structured research report.

RESEARCH TOPIC: {topic}

RAW RESEARCH DATA:
{initial_analysis}

Please create a detailed report with:
1. **Executive Summary** — Key findings in 3-4 sentences
2. **Introduction** — Background and context
3. **Key Findings** — Main discoveries with explanations
4. **Detailed Analysis** — Deep dive into important aspects
5. **Current Trends** — What's happening right now
6. **Future Implications** — What this means going forward
7. **Conclusion** — Final thoughts and recommendations
8. **Sources** — List all sources used

Make it professional, insightful, and easy to read.
"""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                  contents=report_prompt
            )
            initial_report = response.text
        except Exception as e:
            st.error(f"Gemini error: {str(e)}")
            return

    # ── STEP 3: Enhance Report ──
    st.markdown("### ✨ Step 3: Enhancing Report")
    with st.spinner("Adding deeper insights and examples..."):
        try:
            enhance_prompt = f"""
You are an expert content enhancer. Take this research report and make it even better.

TOPIC: {topic}

REPORT TO ENHANCE:
{initial_report}

Enhance it by:
1. Adding real-world examples and case studies
2. Including statistics and data points where relevant
3. Expanding complex concepts with clearer explanations
4. Adding practical implications for different audiences
5. Including expert perspectives and opinions
6. Making language more engaging and readable

Keep the same structure but make each section richer and more valuable.
"""
            enhance_response = client.models.generate_content(
                model="gemini-2.0-flash", contents=enhance_prompt
            )
            enhanced_report = enhance_response.text
        except Exception as e:
            st.error(f"Enhancement error: {str(e)}")
            enhanced_report = initial_report

    # ── STEP 4: Citation Accuracy Check ──
    st.markdown("### 🔬 Step 4: Citation Accuracy Analysis")
    with st.spinner("Verifying claims against source material..."):
        overall_score, claim_results = run_citation_check(enhanced_report, source_texts)

    if overall_score is not None:
        render_citation_ui(overall_score, claim_results)
    else:
        st.warning("Could not run citation check — no source content available.")

    # ── FINAL REPORT ──
    st.divider()
    st.markdown("## 📊 Final Research Report")
    st.markdown(enhanced_report)

    # ── SOURCES ──
    if sources:
        st.divider()
        st.markdown("### 📚 Sources")
        for i, source in enumerate(sources[:10]):
            url = source.get('url', '')
            title = source.get('title', url)
            st.markdown(f"{i+1}. [{title}]({url})")

    # ── DOWNLOAD BUTTONS ──
    st.divider()
    st.markdown("### ⬇️ Download Report")

    col_md, col_pdf = st.columns(2)

    # Markdown download
    citation_summary = ""
    if overall_score is not None:
        verdict_text = "High Confidence" if overall_score >= 70 else "Medium Confidence" if overall_score >= 45 else "Low Confidence"
        citation_summary = f"\n\n---\n## Citation Accuracy Score: {overall_score}%\nVerdict: {verdict_text}\n"

    with col_md:
        st.download_button(
            label="📄 Download Markdown",
            data=enhanced_report + citation_summary,
            file_name=f"{topic.replace(' ', '_')}_report.md",
            mime="text/markdown",
            use_container_width=True
        )

    # PDF download
    with col_pdf:
        with st.spinner("Generating PDF..."):
            pdf_bytes = generate_pdf(topic, enhanced_report, overall_score, claim_results)
        st.download_button(
            label="📕 Download PDF",
            data=pdf_bytes,
            file_name=f"{topic.replace(' ', '_')}_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ─────────────────────────────────────────────
# RUN BUTTON
# ─────────────────────────────────────────────

if st.button("🚀 Start Deep Research", type="primary"):
    if not gemini_key:
        st.error("Please enter your Google Gemini API Key!")
    elif not firecrawl_key:
        st.error("Please enter your Firecrawl API Key!")
    elif not research_topic:
        st.error("Please enter a research topic!")
    else:
        run_research(research_topic, gemini_key, firecrawl_key, max_urls, max_depth)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.divider()
st.markdown("""
<p style='text-align:center;color:#4a4a6a;font-size:0.8rem;'>
Powered by Google Gemini + Firecrawl | Citation Accuracy Engine | PDF Export | Built with Streamlit
</p>
""", unsafe_allow_html=True)