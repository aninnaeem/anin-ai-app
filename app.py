import streamlit as st
from google import genai
import PyPDF2 as pdf
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Anin AI: CV to Cover Letter", page_icon="📄")

# --- INITIALIZE CLIENT ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    # 2026 Standard Client
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("🔑 API Key not found! Add GEMINI_API_KEY to your Streamlit Secrets.")
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

# --- AI GENERATION LOGIC ---
def generate_letter(resume_text, job_desc):
    # Prompt tailored for the Graz/Austrian market
    prompt = f"""
    You are a professional recruitment expert in Graz, Austria. 
    Write a persuasive, high-quality cover letter using the following details.
    
    Current Date: March 2026.
    
    APPLICANT RESUME:
    {resume_text}
    
    TARGET JOB DESCRIPTION:
    {job_desc}
    
    REQUIREMENTS:
    - Highlight the MSc in Data Science (University of Graz) and 6+ years of Software/GIS experience.
    - Mention professional experience with Uttara Bank PLC and technical skills like Python/PyTorch.
    - Tone: Professional, confident, and tailored to the specific job duties.
    """
    
    try:
        # gemini-2.5-flash-lite is the 2026 'throughput' champion for free tier
        # It has a much higher quota (1,000 requests/day) than the Pro versions.
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Quota Limit: Please wait 60 seconds. The 2026 Free Tier is busy."
        return f"⚠️ API Error: {str(e)}"

# --- UI LAYOUT ---
st.title("📄 Anin's AI Cover Letter Pro")
st.caption("Location: Graz, Austria | Engine: Gemini 2.5 Flash-Lite")

st.info("Upload your PDF CV from your computer and paste a job description below.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload CV")
    uploaded_file = st.file_uploader("Choose your Resume (PDF)", type="pdf")
    
with col2:
    st.subheader("2. Job Info")
    job_details = st.text_area("Paste the Job Advertisement text here", height=200, placeholder="Example: We are looking for a Data Scientist at AVL...")

if st.button("🚀 Generate My Letter"):
    if uploaded_file and job_details:
        with st.spinner("Processing PDF and drafting your letter..."):
            # Step 1: Extract text
            cv_text = extract_pdf_text(uploaded_file)
            
            if "Error" in cv_text:
                st.error(cv_text)
            else:
                # Step 2: Generate Letter
                final_letter = generate_letter(cv_text, job_details)
                
                st.markdown("---")
                st.subheader("✉️ Your Tailored Cover Letter")
                st.write(final_letter)
                st.download_button("📥 Download as Text", final_letter, file_name="anin_cover_letter.txt")
    else:
        st.warning("Please provide both a PDF Resume and a Job Description.")
