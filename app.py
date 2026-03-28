import streamlit as st
from google import genai
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Anin AI App", page_icon="✍️")

# --- INITIALIZE CLIENT ---
def get_client():
    try:
        # Pulls from Streamlit Cloud Secrets
        api_key = st.secrets["GEMINI_API_KEY"]
        # In 2026, adding the v1beta option often fixes EU 403/401 errors
        return genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})
    except Exception as e:
        st.error(f"🔑 Secret Error: Check if GEMINI_API_KEY is in Streamlit Secrets. {e}")
        st.stop()

client = get_client()

def generate_letter(resume_text, job_desc):
    # Prompt with Graz, Austria context
    prompt = f"""
    Write a professional cover letter based on this resume and job description.
    Location: Graz, Austria. Date: March 2026.
    
    Resume: {resume_text}
    Job Description: {job_desc}
    """
    
    try:
        # We use gemini-2.0-flash for better 2026 compatibility
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        # This will show the REAL error message in the app UI
        return f"⚠️ API Error: {str(e)}"

# --- UI ---
st.title("🚀 Anin AI Cover Letter Generator")
st.caption("Deployment Location: Graz, Styria | Engine: Gemini 2.0 Flash")

col1, col2 = st.columns(2)
with col1:
    resume = st.text_area("Paste Resume Text", height=250)
with col2:
    job = st.text_area("Paste Job Description", height=250)

if st.button("Generate Cover Letter"):
    if resume and job:
        with st.spinner("AI is thinking..."):
            letter = generate_letter(resume, job)
            st.markdown("---")
            st.markdown(letter)
            st.download_button("Download as Text", letter, file_name="letter.txt")
    else:
        st.warning("Please provide both Resume and Job details.")
