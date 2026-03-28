import streamlit as st
from google import genai
import PyPDF2 as pdf
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Anin AI: CV to Letter", page_icon="📄")

# --- INITIALIZE CLIENT ---
# This pulls the key from your Streamlit Secrets dashboard
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    # We use the standard client without forcing v1beta to avoid 404s
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("🔑 API Key missing! Add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

# --- HELPER: EXTRACT TEXT FROM PDF ---
def extract_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def generate_letter(resume_text, job_desc):
    # Professional prompt for Graz, Austria
    prompt = f"""
    Write a professional cover letter based on the following details.
    Location: Graz, Austria. Current Date: March 2026.
    
    RESUME CONTENT:
    {resume_text}
    
    JOB DESCRIPTION:
    {job_desc}
    """
    try:
        # gemini-2.0-flash is the 2026 workhorse model
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Quota full. Please wait 60 seconds and try again."
        return f"⚠️ AI Error: {str(e)}"

# --- UI ---
st.title("📄 Smart Cover Letter Generator")
st.markdown("Upload your CV and paste a job description to get a tailored letter.")

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Your Resume")
    uploaded_cv = st.file_uploader("Upload CV (PDF)", type="pdf")
    
with col2:
    st.subheader("2. Job Details")
    job_input = st.text_area("Paste Job Description here...", height=200)

if st.button("🚀 Generate Cover Letter"):
    if uploaded_cv and job_input:
        with st.spinner("Extracting text and writing letter..."):
            # Step 1: Read the PDF
            resume_text = extract_pdf_text(uploaded_cv)
            
            if "Error" in resume_text:
                st.error(resume_text)
            else:
                # Step 2: Generate with Gemini
                letter = generate_letter(resume_text, job_input)
                
                st.markdown("---")
                st.subheader("✉️ Tailored Cover Letter")
                st.write(letter)
                st.download_button("📥 Download as Text", letter, file_name="cover_letter.txt")
    else:
        st.warning("Please upload your PDF CV and paste the job description first.")
