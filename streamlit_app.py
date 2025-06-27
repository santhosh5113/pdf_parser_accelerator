import streamlit as st
import os
import tempfile
import subprocess
import json

st.set_page_config(layout="wide", page_title="PDF Parser Accelerator")

# ==== CUSTOM CSS FOR DARK THEME + STYLING ====
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #10131A;
        color: #E0E0E0;
    }
    h1, h2, h3, h4 {
        color: #21cbf3;
        font-weight: 800;
        letter-spacing: 0.01em;
        margin-bottom: 0.5em;
    }
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #21cbf3;
        margin-bottom: 0.7em;
        margin-top: 1.5em;
        letter-spacing: 0.01em;
        text-align: center;
    }
    .vector-card-dark {
        background: #181C24;
        border-radius: 14px;
        border: 2px solid #21cbf3;
        box-shadow: 0 4px 24px rgba(33,203,243,0.10);
        padding: 1.2rem 0.7rem 1.2rem 0.7rem;
        margin-bottom: 1.2rem;
        text-align: center;
        min-width: 220px;
        max-width: 220px;
        min-height: 210px;
        max-height: 210px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: box-shadow 0.2s, border 0.2s, transform 0.2s;
        cursor: pointer;
    }
    .vector-card-dark:hover, .vector-card-dark:focus {
        box-shadow: 0 8px 32px rgba(33,203,243,0.22);
        border: 2px solid #1976d2;
        transform: translateY(-4px) scale(1.04);
    }
    .stButton>button {
        background: linear-gradient(90deg, #1976d2 0%, #21cbf3 100%) !important;
        color: #fff !important;
        border-radius: 10px;
        padding: 0.7em 2em;
        font-weight: 700;
        font-size: 1.1rem;
        margin-top: 1.2em;
        margin-bottom: 1.2em;
        border: none;
        box-shadow: 0 2px 8px rgba(25,118,210,0.12);
        transition: background 0.2s, box-shadow 0.2s, transform 0.2s;
    }
    .stButton>button:hover, .stButton>button:focus {
        background: linear-gradient(90deg, #21cbf3 0%, #1976d2 100%) !important;
        box-shadow: 0 4px 16px rgba(33,203,243,0.18);
        transform: scale(1.04);
    }
    .stSelectbox>div>div, .stFileUploader>div {
        background-color: #181C24 !important;
        color: #E0E0E0 !important;
        border-radius: 8px;
        font-size: 1.05em;
    }
    .stSelectbox label, .stFileUploader label {
        color: #21cbf3 !important;
        font-weight: 600;
    }
    code {
        background: #23272F;
        color: #90CAF9;
        padding: 0.2em 0.4em;
        border-radius: 4px;
        font-size: 1em;
    }
    .stTextInput>div>input, .stNumberInput>div>input {
        background-color: #181C24 !important;
        color: #E0E0E0 !important;
        border-radius: 8px !important;
        font-size: 1em;
    }
    .stAlert, .stInfo, .stWarning, .stError, .stSuccess {
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; font-size:2.5rem; font-weight:900; margin-bottom:0.2em; color:#21cbf3; letter-spacing:0.01em; text-shadow:0 2px 12px #111;'>🚀 PDF Parser Accelerator</h1>", unsafe_allow_html=True)

# ==== FILE UPLOADER ====
st.markdown("<div class='section-title'>📄 Upload Your PDF</div>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# ==== CHUNKING OPTIONS ====
st.markdown("<div class='section-title'>✂️ Chunking Options</div>", unsafe_allow_html=True)
with st.expander("⚙️ Advanced Settings", expanded=True):
    chunk_cols = st.columns(2)
    with chunk_cols[0]:
        chunk_size = st.selectbox("Chunk Size", [256, 512, 1024, 2048], index=1,
                                  help="Number of tokens per chunk", format_func=lambda x: f"{x} tokens")
    with chunk_cols[1]:
        chunk_overlap = st.selectbox("Chunk Overlap", [0, 32, 64, 128], index=1,
                                     help="Overlap between chunks", format_func=lambda x: f"{x} tokens")
    st.session_state['chunk_size'] = chunk_size
    st.session_state['chunk_overlap'] = chunk_overlap

# ==== EMBEDDING CARD ====
st.markdown("<div class='section-title'>🧬 Embedding Model</div>", unsafe_allow_html=True)
st.markdown("""
<div class='vector-card-dark' tabindex='0'>
    <div style='font-size:2.2rem; color:#21cbf3; margin-bottom:0.2em; text-shadow:0 2px 8px #111;'>🧬</div>
    <div style='font-weight:900; font-size:1.18em; margin-bottom:0.08em; color:#fff;'>Embeddings</div>
    <div style='font-size:1.01em; color:#e0e0e0; margin-bottom:0.07em; text-align:center;'>Model: <code>sentence-transformers/all-MiniLM-L6-v2</code></div>
    <div style='font-size:0.91em; color:#90caf9; text-align:center;'>Library: <code>sentence-transformers</code> (HuggingFace + PyTorch)</div>
</div>
""", unsafe_allow_html=True)

# ==== VECTOR DB CARDS ====
st.markdown("<div class='section-title'>🧠 Choose a Vector Database</div>", unsafe_allow_html=True)
VECTOR_DB_CARDS = [
    {"icon": "🧪", "name": "chroma", "title": "Best for Prototyping", "description": "Plug-and-play for local dev. #local #easy"},
    {"icon": "⚡", "name": "faiss", "title": "Blazing Fast Search", "description": "High-speed local vector search. #fastest #scalable"},
    {"icon": "🔎", "name": "qdrant", "title": "Smart Filters", "description": "Production-ready & filterable. #semantic #docker"},
    {"icon": "☁️", "name": "milvus", "title": "Cloud Native Scale", "description": "Distributed and scalable. #cloud #enterprise"},
    {"icon": "🕸️", "name": "weaviate", "title": "Hybrid Search", "description": "GraphQL & hybrid vector DB. #hybrid #modular"},
]
cols = st.columns(len(VECTOR_DB_CARDS))
for i, card in enumerate(VECTOR_DB_CARDS):
    with cols[i]:
        st.markdown(f"""
        <div class='vector-card-dark' tabindex='0'>
            <div style='font-size:2rem; color:#21cbf3; margin-bottom:0.15em'>{card['icon']}</div>
            <div style='font-weight:900; font-size:1.13em; color:#fff; margin-bottom:0.08em'>{card['name'].capitalize()}</div>
            <div style='font-size:0.98em; color:#e0e0e0; margin-bottom:0.09em; text-align:center;'>{card['title']}</div>
            <div style='font-size:0.91em; color:#90caf9; text-align:center;'>{card['description']}</div>
        </div>
        """, unsafe_allow_html=True)

# Use the lowercase backend name for the pipeline
vector_store_display_names = [c['name'].capitalize() for c in VECTOR_DB_CARDS]
vector_store_idx = 0
if 'vector_store' in st.session_state:
    try:
        vector_store_idx = vector_store_display_names.index(st.session_state['vector_store'])
    except Exception:
        vector_store_idx = 0
vector_store_display = st.selectbox("Select Vector Store Backend", vector_store_display_names, index=vector_store_idx)
vector_store = next(c['name'] for c in VECTOR_DB_CARDS if c['name'].capitalize() == vector_store_display)
st.session_state['vector_store'] = vector_store_display

# ==== PARSE BUTTON ====
st.markdown("<div style='display:flex; justify-content:center; margin-top:2em; margin-bottom:2em;'>", unsafe_allow_html=True)
if 'pipeline_running' not in st.session_state:
    st.session_state['pipeline_running'] = False
run_button = st.button("Parse PDF", disabled=st.session_state['pipeline_running'])
st.markdown("</div>", unsafe_allow_html=True)

# ==== PARSING PIPELINE ====
if uploaded_file and run_button and not st.session_state['pipeline_running']:
    st.session_state['pipeline_running'] = True
    with st.spinner("Running parsing pipeline... Please wait."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(uploaded_file.read())
            tmp_pdf_path = tmp_pdf.name

        output_json = os.path.join("shared/output_json", f"{os.path.basename(tmp_pdf_path)}.json")

        cmd = [
            "python", "-m", "database.run_pipeline",
            tmp_pdf_path, output_json,
            "--vector-store", vector_store,
            "--chunk-size", str(chunk_size),
            "--chunk-overlap", str(chunk_overlap)
        ]

        st.write("⏳ Parsing in progress...")
        output_lines = []
        output_container = st.empty()
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env) as proc:
            for line in proc.stdout:
                output_lines.append(line.rstrip())
                output_container.text('\n'.join(output_lines))
            proc.wait()

    st.session_state['pipeline_running'] = False

    phase1_lines, phase2_lines = [], []
    phase = 1
    for line in output_lines:
        if "[DEBUG] Current CONDA_DEFAULT_ENV:" in line and "vector store" in line:
            phase = 2
        (phase1_lines if phase == 1 else phase2_lines).append(line)

    st.success("✅ PDF Parsed Successfully!")
    st.subheader("📊 Phase 1: Parsing Output")
    st.text("\n".join(phase1_lines))
    st.subheader("🗃️ Phase 2: Vector Storage")
    st.text("\n".join(phase2_lines))

    if os.path.exists(output_json):
        with open(output_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.markdown("### 📦 Extracted Data Preview")
        st.write("Output JSON keys:", list(data.keys()))
        if "text" in data:
            st.code(data["text"][:500], language="markdown")
