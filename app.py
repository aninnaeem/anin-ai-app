import streamlit as st
from google import genai
import PyPDF2 as pdf

# --- PAGE CONFIG ---
st.set_page_config(page_title="Anin's AI Letter Gen", page_icon="✍️")

# --- INITIALIZE CLIENT ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("🔑 API Key missing in Streamlit Secrets!")
    st.stop()

def extract_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    return "".join([page.extract_text() for page in reader.pages])

def generate_letter(resume_text, job_desc):
    # This stricter prompt forces the AI to ACT as a writer, not a copier
    prompt = f"""
    You are an expert Career Coach in Graz, Austria. 
    TASK: Write a highly professional, persuasive Cover Letter for the applicant below.
    
    APPLICANT DETAILS (RESUME):
    {resume_text}
    
    TARGET JOB DESCRIPTION:
    {job_desc}
    
    GUIDELINES:
    1. Use a professional business format.
    2. Address: Graz, Austria. Date: {st.date_input("Select Date", help="Today's Date").strftime('%B %d, %2026')}.
    3. Highlight the applicant's MSc in Data Science at Uni Graz and their 6+ years of Software/GIS experience.
    4. Mention their German skills (A1-A2) and their background with Uttara Bank PLC.
    5. DO NOT just repeat the CV. Connect their skills to the specific job requirements.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- UI ---
st.title("✍️ Anin's Smart Cover Letter Gen")
st.markdown("Professional AI for the Graz Job Market")

uploaded_cv = st.file_uploader("Upload your CV (PDF)", type="pdf")
job_input = st.text_area("Paste the Job Description (The job you want)", height=200, placeholder="Example: Software Engineer at AVL or Data Scientist at Dynatrace...")

if st.button("Generate My Cover Letter"):
    if uploaded_cv and job_input:
        with st.spinner("Writing a tailored letter for you..."):
            resume_text = extract_pdf_text(uploaded_cv)
            letter = generate_letter(resume_text, job_input)
            
            st.success("Letter Generated!")
            st.markdown("---")
            st.write(letter)
            st.download_button("Download Letter", letter, file_name="Anin_Cover_Letter.txt")
    else:
        st.warning("Please upload your PDF and paste a Job Description first!")
