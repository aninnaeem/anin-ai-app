import streamlit as st
from google import genai
import PyPDF2 as pdf
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Anin AI: PDF to Letter", page_icon="📄")

# --- INITIALIZE CLIENT ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("🔑 Please add your GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

# --- HELPER: EXTRACT TEXT FROM PDF ---
def extract_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

def generate_letter(resume_text, job_desc):
    prompt = f"""
    Context: Applicant is based in Graz, Austria. Date: March 2026.
    Task: Write a professional cover letter based on the Resume and Job Description below.
    
    RESUME:
    {resume_text}
    
    JOB DESCRIPTION:
    {job_desc}
    """
    try:
        # gemini-1.5-flash often has better free-tier availability than 2.0 when 429 occurs
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ ERROR: You've hit the Google Free Tier limit. Please wait 60 seconds and try again."
        return f"⚠️ API Error: {str(e)}"

# --- UI ---
st.title("📄 PDF Resume → Cover Letter")
st.info("Location: Graz, Styria | Engine: Gemini Flash")

# File Uploader
uploaded_cv = st.file_uploader("Upload your CV (PDF)", type="pdf")
job_input = st.text_area("Paste the Job Description here", height=200)

if st.button("Generate My Letter"):
    if uploaded_cv and job_input:
        with st.spinner("Reading PDF and writing letter..."):
            # Step 1: Extract text from the uploaded PDF
            resume_text = extract_pdf_text(uploaded_cv)
            
            # Step 2: Send to AI
            letter = generate_letter(resume_text, job_input)
            
            st.markdown("### Your Generated Cover Letter")
            st.write(letter)
            st.download_button("Download as Text", letter, file_name="anin_cover_letter.txt")
    else:
        st.warning("Please upload a PDF CV and paste a Job Description.")
