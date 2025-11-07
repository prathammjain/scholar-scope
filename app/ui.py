import streamlit as st
import requests
import os
import sys

sys.path.insert(0, os.path.abspath('.'))

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="ScholarScope · AI Research Copilot",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Global styles: Space‑black + refined scale ----
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

      :root {
        --black-0: #000;           /* true black */
        --black-1: #0a0a0a;        /* app bg */
        --black-2: #111;           /* panels */
        --black-3: #181818;        /* inputs */
        --line:    #2a2a2a;        /* borders */
        --muted:   #9aa0a6;        /* captions */
        --text:    #e6e6e6;        /* body */
        --accent:  #f3d26a;        /* warm gold */
        --accent-2:#ffb84d;        /* secondary */
      }

      * { font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }

      /* App containers */
      [data-testid="stAppViewContainer"] {
        background: radial-gradient(1200px 600px at 20% 0%, rgba(243,210,106,0.06), transparent 60%),
                    radial-gradient(800px 400px at 90% -10%, rgba(255,184,77,0.05), transparent 50%),
                    var(--black-1);
      }
      [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a 0%, #121212 100%);
        border-right: 1px solid var(--line);
      }

      /* Type scale: tighter, no oversized headings */
      h1, h2, h3, h4 { letter-spacing: -0.02em !important; }
      h1 { color: var(--text) !important; font-weight: 800 !important; font-size: 2.2rem !important; margin: 0 0 .25rem 0 !important; }
      h2 { color: var(--text) !important; font-weight: 700 !important; font-size: 1.4rem !important; }
      h3 { color: var(--text) !important; font-weight: 700 !important; font-size: 1.1rem !important; }
      h4 { color: var(--text) !important; font-weight: 600 !important; font-size: 1rem !important; }

      p, .stMarkdown, label, span, li { color: var(--text) !important; }
      small, .help, .caption, .stCaption, .st-emotion-cache-1lb3x6j { color: var(--muted) !important; }

      /* Brand accent line */
      .accent-line { height: 1px; background: linear-gradient(90deg, var(--accent), transparent); margin: 12px 0 24px 0; }

      /* Inputs */
      .stTextInput input, .stTextArea textarea {
        background: var(--black-3) !important; border: 1px solid var(--line) !important; color: var(--text) !important;
        border-radius: 10px !important; padding: 12px 14px !important; font-size: 0.95rem !important; transition: 0.2s ease !important;
      }
      .stTextInput input:focus, .stTextArea textarea:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(243,210,106,0.12) !important; }
      .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #6e6e6e !important; }

      /* Buttons */
      .stButton button, [data-testid="baseButton-secondary"] {
        background: linear-gradient(135deg, var(--accent), var(--accent-2)) !important;
        color: #000 !important; border: 0 !important; border-radius: 10px !important; padding: 10px 18px !important;
        font-weight: 800 !important; font-size: 0.9rem !important; letter-spacing: 0.02em !important; text-transform: uppercase !important;
        box-shadow: 0 8px 24px rgba(243,210,106,0.18) !important; transition: transform .12s ease, box-shadow .2s ease !important;
      }
      .stButton button:hover { transform: translateY(-1px) !important; box-shadow: 0 10px 28px rgba(243,210,106,0.24) !important; }

      /* Metrics */
      [data-testid="stMetric"] { background: #101010; border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; }
      [data-testid="stMetricValue"] { color: var(--accent) !important; font-size: 1.35rem !important; font-weight: 900 !important; }
      [data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: .08em; }

      /* Tabs */
      .stTabs [data-baseweb="tab-list"] { gap: 2px; border-bottom: 1px solid var(--line); }
      .stTabs [data-baseweb="tab"] { color: #8c8c8c; padding: 12px 18px !important; border-bottom: 2px solid transparent; font-weight: 700; text-transform: uppercase; font-size: .8rem; }
      .stTabs [aria-selected="true"] { color: var(--accent); border-bottom: 2px solid var(--accent); }

      /* Cards */
      .card { background: linear-gradient(180deg, #111 0%, #0e0e0e 100%); border: 1px solid var(--line); border-radius: 14px; padding: 18px; }
      .card:hover { border-color: var(--accent); box-shadow: 0 12px 40px rgba(243,210,106,0.08); }

      /* File uploader */
      [data-testid="stFileUploader"] { background: #111 !important; border: 1px dashed var(--line) !important; border-radius: 12px !important; padding: 24px !important; }
      [data-testid="stFileUploader"]:hover { border-color: var(--accent) !important; }

      /* Chat bubbles */
      .chat-user { background: #101010; border: 1px solid var(--line); border-left: 3px solid var(--accent); padding: 14px 16px; border-radius: 12px; }
      .chat-ai   { background: #0e0e0e; border: 1px solid var(--line); border-left: 3px solid #5a5a5a; padding: 14px 16px; border-radius: 12px; }

      /* Scrollbar */
      ::-webkit-scrollbar { width: 10px; height: 10px; }
      ::-webkit-scrollbar-track { background: #0a0a0a; }
      ::-webkit-scrollbar-thumb { background: #2d2d2d; border-radius: 6px; }
      ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

      /* Links */
      .stLinkButton a { background: #111 !important; border: 1px solid var(--line) !important; color: var(--accent) !important; border-radius: 10px !important; padding: 10px 14px !important; text-decoration: none !important; }
      .stLinkButton a:hover { border-color: var(--accent) !important; }

      /* Subtle container padding tweaks */
      .block-container { padding-top: 1.2rem; padding-bottom: 3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Session state ----
if 'pdf_chunks' not in st.session_state:
    st.session_state.pdf_chunks = None
if 'pdf_embeddings' not in st.session_state:
    st.session_state.pdf_embeddings = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ---- Helpers ----
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def get_index_stats():
    try:
        response = requests.get(f"{API_URL}/stats", timeout=8)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None


def search_papers(query, top_k=5):
    try:
        response = requests.post(
            f"{API_URL}/search",
            json={"query": query, "top_k": top_k},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def generate_search_summary(query, results):
    try:
        from ingestion.llm_handler import get_llm_handler

        llm = get_llm_handler()
        papers_context = []
        for i, result in enumerate(results.get('results', [])[:3], 1):
            papers_context.append(
                f"Paper {i}: {result['title']}\nAuthors: {result.get('authors', 'Unknown')}\nAbstract: {result['abstract'][:400]}..."
            )

        prompt = (
            f"You are a research assistant. User searched: \"{query}\"\n\n"
            f"Papers:\n" + "\n\n".join(papers_context) +
            "\n\nGive a brief insight (under 90 words) on why these matter and key themes."
        )

        response = llm.client.chat.completions.create(
            model=llm.model,
            messages=[
                {"role": "system", "content": "You are a concise research assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=180,
        )
        return response.choices[0].message.content
    except Exception:
        return None

# ---- Header ----
left, right = st.columns([6, 1])
with left:
    st.markdown("<h1>ScholarScope</h1>", unsafe_allow_html=True)
    st.caption("AI‑powered research intelligence. Space‑black. No fluff.")
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
with right:
    online = check_api_health()
    st.metric(label="Status", value=("Online" if online else "Offline"))

# ---- Sidebar ----
with st.sidebar:
    st.markdown("### Control panel")
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)

    if online:
        st.success("⚡ System online")
    else:
        st.error("⚠ System offline")

    stats = get_index_stats()
    if stats:
        st.markdown("### Database")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Docs", f"{stats.get('total_documents', 0)}")
        with c2: st.metric("Dim", stats.get('embedding_dimension', '—'))
        with c3: st.metric("Model", stats.get('model_name', 'N/A'))

    st.markdown("---")
    st.markdown("### Settings")
    top_k = st.slider("Results", 1, 20, 5)
    use_ai_summary = st.checkbox("AI insights", value=True)

    st.markdown("---")
    st.caption("Powered by FastAPI • FAISS • Your LLM stack")

# ---- Tabs ----
tab1, tab2 = st.tabs(["Search database", "Chat with PDF"])  # compact, no shouting

# TAB 1 — Search
with tab1:
    st.markdown("#### Search research papers")
    i1, i2 = st.columns([6, 1])
    with i1:
        query = st.text_input(
            label="search",
            placeholder="Enter your research query…",
            key="search_query",
            label_visibility="collapsed",
        )
    with i2:
        search_btn = st.button("Search", type="primary", use_container_width=True)

    if search_btn and query:
        with st.spinner("Searching database…"):
            results = search_papers(query, top_k)

        if results:
            st.success(f"Found {results.get('total_results', 0)} papers · {results.get('latency_ms', 0):.0f} ms")

            if use_ai_summary and results.get('total_results', 0) > 0:
                with st.spinner("Generating insights…"):
                    summary = generate_search_summary(query, results)
                if summary:
                    st.markdown(
                        f"""
                        <div class="card">
                          <h4 style="margin:0 0 8px 0; color: var(--accent)">AI insights</h4>
                          <p style="margin:0; line-height:1.7; color:#d8d8d8">{summary}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            for result in results.get('results', []):
                st.markdown(
                    f"""
                    <div class="card">
                      <div style="display:flex; gap:16px; align-items:flex-start; justify-content:space-between">
                        <div style="flex:1">
                          <div style="color:#8c8c8c; font-size:11px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px">Paper #{result.get('rank','')}</div>
                          <h3 style="margin:0 0 6px 0">{result.get('title','Untitled')}</h3>
                          <p style="color:#9aa0a6; margin:0 0 2px 0; font-size:13px">{result.get('authors','Unknown')[:140]}{'…' if len(result.get('authors',''))>140 else ''}</p>
                          <p style="color:#7c7c7c; margin:0 0 10px 0; font-size:12px">{result.get('categories','N/A')}</p>
                          <p style="color:#c9c9c9; margin:0; line-height:1.7; font-size:14px">{result.get('abstract','')[:380]}{'…' if len(result.get('abstract',''))>380 else ''}</p>
                        </div>
                        <div style="min-width:108px; text-align:center">
                          <div style="background:linear-gradient(135deg, var(--accent), var(--accent-2)); color:#000; padding:12px 14px; border-radius:10px; font-weight:900; box-shadow:0 4px 16px rgba(243,210,106,.25)">
                            <div style="font-size:22px; line-height:1">{result.get('score',0):.2f}</div>
                            <div style="font-size:10px; opacity:.8; letter-spacing:.08em; text-transform:uppercase">Relevance</div>
                          </div>
                        </div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if result.get('pdf_url'):
                    st.link_button("View paper →", result['pdf_url'])
    elif search_btn:
        st.warning("Enter a search query")

    with st.expander("Example queries"):
        st.markdown(
            """
            • Attention mechanisms in neural networks  
            • Graph neural networks for drug discovery  
            • Transfer learning in computer vision  
            • Reinforcement learning for robotics  
            • Large language model fine‑tuning
            """
        )

# TAB 2 — Chat with PDF
with tab2:
    st.markdown("#### Upload research paper")

    uploaded_file = st.file_uploader("pdf", type="pdf", label_visibility="collapsed")

    if uploaded_file:
        if st.button("Process PDF", type="primary"):
            with st.spinner("Processing document…"):
                try:
                    from ingestion.pdf_processor import get_pdf_processor

                    processor = get_pdf_processor()
                    chunks = processor.extract_text_from_pdf(uploaded_file)
                    st.success(f"Extracted {len(chunks)} text segments")

                    embeddings, chunks = processor.create_embeddings(chunks)

                    st.session_state.pdf_chunks = chunks
                    st.session_state.pdf_embeddings = embeddings
                    st.session_state.chat_history = []

                    st.success("Ready for questions")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if st.session_state.pdf_chunks:
        st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
        st.markdown("#### Conversation")

        for chat in st.session_state.chat_history:
            st.markdown(
                f"""
                <div class="chat-user">
                  <div style=\"color: var(--accent); font-size:11px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px\">You</div>
                  <div>{chat['question']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="chat-ai">
                  <div style=\"color:#9aa0a6; font-size:11px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px\">AI assistant</div>
                  <div style=\"line-height:1.8\">{chat['answer']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if chat.get('sources'):
                with st.expander("View sources"):
                    for src in chat['sources']:
                        st.caption(f"Page {src.get('page','?')} • {src.get('score',0):.2f}")
                        st.text(src.get('text','')[:250])

        with st.form(key='chat', clear_on_submit=True):
            question = st.text_input(
                "q",
                placeholder="Ask anything about the paper…",
                key="q",
                label_visibility="collapsed",
            )
            submit = st.form_submit_button("Send", type="primary", use_container_width=True)

            if submit and question:
                try:
                    from ingestion.pdf_processor import get_pdf_processor
                    from ingestion.llm_handler import get_llm_handler

                    processor = get_pdf_processor()
                    llm = get_llm_handler()

                    with st.spinner("Analyzing…"):
                        chunks = processor.search_chunks(
                            question,
                            st.session_state.pdf_embeddings,
                            st.session_state.pdf_chunks,
                            top_k=3,
                        )
                        answer = llm.generate_answer(question, chunks)

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "sources": chunks,
                    })

                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Upload a PDF to begin")

# ---- Footer ----
st.markdown("""
  <div style='margin-top:24px; color:#666; font-size:12px;'>
    Tip: Press <strong>/</strong> to focus the search bar. Keep queries short. Let relevance do the heavy lifting.
  </div>
""", unsafe_allow_html=True)
