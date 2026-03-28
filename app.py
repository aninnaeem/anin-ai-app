import streamlit as st
from google import genai
from docx import Document
from io import BytesIO
import PyPDF2
from datetime import datetime

# PWA Metadata
st.set_page_config(page_title="Anin Naeem AI", page_icon="📝")
st.markdown('<link rel="manifest" href="./manifest.json">', unsafe_allow_html=True)

# Secure API Key from Streamlit Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception:
    st.error("API Key missing! Please add it to Streamlit Secrets.")
    st.stop()

def extract_text(file):
    reader = PyPDF2.PdfReader(file)
    return "".join([p.extract_text() for p in reader.pages])

def generate_letter(cv, job):
    date = datetime.now().strftime("%B %d, %Y")
    prompt = f"Write a professional cover letter for Md. Anin Naeem (Graz, Austria) dated {date}. CV: {cv} Job: {job}"
    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
    return response.text

st.title("📄 AI Cover Letter Pro")
st.caption("Portable Web App by Md. Anin Naeem")

file = st.file_uploader("Upload CV (PDF)", type="pdf")
job = st.text_area("Paste Job Requirements")

if st.button("Generate My Letter"):
    if file and job:
        with st.spinner("Gemini is writing..."):
            res = generate_letter(extract_text(file), job)
            st.session_state['out'] = res
            st.markdown("---")
            st.write(res)

if 'out' in st.session_state:
    doc = Document()
    doc.add_paragraph(st.session_state['out'])
    bio = BytesIO()
    doc.save(bio)
    st.download_button("📥 Download Word (.docx)", bio.getvalue(), "CoverLetter.docx")
