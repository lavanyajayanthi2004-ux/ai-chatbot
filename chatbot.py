import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
import time

# ======================
# ENV SETUP
# ======================
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error("❌ GROQ_API_KEY not found")
    st.stop()

client = Groq(api_key=API_KEY)
MODEL_NAME = "llama-3.1-8b-instant"

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="AI PDF Chatbot",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ======================
# CSS (CLEAN + PROFESSIONAL)
# ======================
st.markdown("""
<style>
body {
    background-color: #020617;
}

.app-container {
    max-width: 900px;
    margin: auto;
    padding-bottom: 80px;
}

/* Header */
.header-card {
    padding: 34px;
    border-radius: 22px;
    background: radial-gradient(
        120% 120% at 50% 0%,
        rgba(37, 99, 235, 0.10),
        rgba(2, 6, 23, 0.95)
    );
    box-shadow:
        0 0 0 1px rgba(148, 163, 184, 0.08),
        0 20px 40px rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(8px);
    margin-bottom: 28px;
}


/* Chat container */
.chat-container {
    margin-top: 20px;
}

/* User bubble */
.user-bubble {
    background: linear-gradient(135deg, #2563eb, #1e40af);
    color: white;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 12px 0;
    max-width: 70%;
    float: right;
    clear: both;
}

/* Bot bubble */
.bot-bubble {
    background: #0f172a;
    border: 1px solid #1e293b;
    color: #e5e7eb;
    padding: 14px 18px;
    border-radius: 14px;
    margin: 12px 0;
    max-width: 80%;
    float: left;
    clear: both;
    line-height: 1.7;
    box-shadow: 0 4px 12px rgba(0,0,0,0.35);
}

/* File badge */
.file-badge {
    background: #020617;
    border: 1px solid #1e293b;
    padding: 8px 14px;
    border-radius: 10px;
    color: #cbd5f5;
    display: inline-block;
    margin-bottom: 10px;
}

/* Typing */
.typing {
    color: #94a3b8;
    font-style: italic;
}

/* Chat input alignment */
[data-testid="stChatInput"] {
    max-width: 900px;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)

# ======================
# SESSION STATE
# ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

# ======================
# DETECT IF USER HAS STARTED TO CHAT
# ======================
def has_user_message():
    return any(msg["role"] == "user" for msg in st.session_state.messages)


# ======================
# PDF TEXT EXTRACTION
# ======================
def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(" ".join(text.split()))
    return " ".join(pages)

# ======================
# SIDEBAR (PDF UPLOAD)
# ======================
with st.sidebar:
    st.markdown("## 📄 PDF Document")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file:
        text = extract_pdf_text(uploaded_file)
        if text.strip():
            st.session_state.pdf_text = text[:6000]
            st.session_state.pdf_name = uploaded_file.name
            st.success("PDF loaded successfully")
        else:
            st.error("This PDF has no readable text")

    if st.session_state.pdf_name:
        st.markdown(f"**Loaded:** {st.session_state.pdf_name}")
        if st.button("🗑 Remove PDF"):
            st.session_state.pdf_text = ""
            st.session_state.pdf_name = ""
            st.rerun()

# ======================
# MAIN UI
# ======================
st.markdown("<div class='app-container'>", unsafe_allow_html=True)

# HEADER
if not has_user_message():
    st.markdown("""
    <div class="header-card">
        <h1 style="
            text-align:center;
            color:#e5e7eb;
            font-weight:600;
            letter-spacing:0.3px;
            margin-bottom:10px;
        ">
            🤖 Your Assistant
        </h1>
        <p style="
            text-align:center;
            color:#9ca3af;
            font-size:15px;
            max-width:560px;
            margin:auto;
            line-height:1.6;
        ">
            Upload a PDF and ask questions.  
            Answers are based on the document and general knowledge.
        </p>
    </div>
    """, unsafe_allow_html=True)



# # INITIAL MESSAGE
# if not st.session_state.messages:
#     st.session_state.messages.append({
#         "role": "assistant",
#         "content":
#     })

# FILE BADGE
if st.session_state.pdf_name:
    st.markdown(
        f"<div class='file-badge'>📎 {st.session_state.pdf_name}</div>",
        unsafe_allow_html=True
    )

# CHAT DISPLAY
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-bubble'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='bot-bubble'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# ======================
# CHAT INPUT
# ======================
user_input = st.chat_input("Type your message and press Enter")

def build_conversation(system_prompt, pdf_text, messages, user_input, max_history=6):
    convo = [{"role": "system", "content": system_prompt}]

    # Add recent chat history (illusion of memory)
    for msg in messages[-max_history:]:
        convo.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Attach PDF context only to the current user query
    if pdf_text:
        user_input = f"""
You have access to the following PDF content.
Use it only when relevant.

PDF CONTENT:
{pdf_text}

USER MESSAGE:
{user_input}
"""

    convo.append({"role": "user", "content": user_input})
    return convo


# ======================
# CHAT LOGIC
# ======================
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        for dots in ["Typing.", "Typing..", "Typing..."]:
            placeholder.markdown(
                f"<div class='typing'>{dots}</div>",
                unsafe_allow_html=True
            )
            time.sleep(0.25)

    system_prompt = (
        "You are a helpful assistant. "
        "If PDF content is provided, use it when relevant."
    )

    if st.session_state.pdf_text:
        user_prompt = f"""
PDF CONTENT:
{st.session_state.pdf_text}

USER QUESTION:
{user_input}
"""
    else:
        user_prompt = user_input

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages = build_conversation(
    system_prompt=system_prompt,
    pdf_text=st.session_state.pdf_text,
    messages=st.session_state.messages,
    user_input=user_input,
    max_history=6
)
,
        temperature=0.6,
        max_tokens=700
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
