# AI PDF Chatbot

An elegant AI-powered chatbot built with **Streamlit** that allows users to upload a PDF and ask questions.  
The assistant answers using **PDF content + conversational context**, creating a natural chat experience with memory illusion.

---

## Features

- Upload and read PDF documents
- Chat-based question answering
- Conversational memory (recent context replay)
- Modern dark UI with smooth UX
- Welcome header disappears after first message
- Powered by Groq (LLaMA 3.1)

---

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: LLaMA 3.1 (via Groq API)
- **PDF Parsing**: PyPDF2
- **Environment Management**: python-dotenv

---

## Project Structure

```text
.
├── app.py               # Main Streamlit app
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── .env                 # API keys (not committed)
└── .gitignore


