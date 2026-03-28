import streamlit as st
from google import genai
import PyPDF2 as pdf
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Anin AI: Cover Letter Pro", page_icon="✍️", layout="wide")

# --- INITIALIZE AI CLIENT ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    # 2026 Stable SDK Client
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("🔑 API Key missing! Add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

# --- HELPERS ---
def extract_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content: text += content
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def generate_letter(resume_text, job_desc):
    # This prompt is optimized to be short (saves your quota/tokens)
    current_date = datetime.now().strftime("%B %d, %2026")
    prompt = f"""
    You are a career expert in Graz, Austria. Write a professional cover letter.
    Date: {current_date}
    Applicant: Md. Anin Naeem (MSc Data Science Candidate, Uni Graz)
    
    RESUME: {resume_text[:2000]} # Limit text to save quota
    JOB: {job_desc[:1500]}
    
    Format: Professional Business Letter. 
    Focus: 6+ years experience, Software/GIS background, and current studies in Graz.
    """
    try:
        # gemini-2.0-flash-lite is the 'Safety Model' for 2026 free tiers
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Quota Exhausted: Google's free tier is busy. Please wait 1 minute."
        return f"⚠️ AI Error: {str(e)}"

# --- UI INTERFACE ---
st.title("🚀 Anin's AI Cover Letter Pro")
st.markdown(f"**Location:** Graz, Austria | **Date:** {datetime.now().strftime('%d %B %Y')}")

# Column Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Your Background")
    tab1, tab2 = st.tabs(["Upload PDF", "Paste Text"])
    
    with tab1:
        uploaded_file = st.file_uploader("Upload CV (PDF)", type="pdf")
    with tab2:
        manual_resume = st.text_area("Or paste CV text here", height=200)

with col2:
    st.subheader("2. The Job")
    job_details = st.text_area("Paste the Job Description here", height=275, placeholder="What job are you applying for?")

# Action Button
if st.button("✨ Generate My Professional Letter"):
    # Determine which resume source to use
    final_resume_text = ""
    if uploaded_file:
        final_resume_text = extract_pdf_text(uploaded_file)
    elif manual_resume:
        final_resume_text = manual_resume
        
    if final_resume_text and job_details:
        with st.spinner("Analyzing data and drafting letter..."):
            letter = generate_letter(final_resume_text, job_details)
            st.success("Draft Ready!")
            st.markdown("---")
            st.subheader("✉️ Your Tailored Cover Letter")
            st.markdown(letter)
            st.download_button("📥 Download as Text File", letter, file_name="Anin_Cover_Letter.txt")
    else:
        st.warning("Please provide your CV (PDF or Text) and the Job Description!")
