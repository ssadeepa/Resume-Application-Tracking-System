import os
import io
import base64
from PIL import Image
import pdf2image
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Google API key for generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate a response using the Gemini model
def generate_gemini_response(job_description, resume_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([job_description, resume_content[0], prompt])
    return response.text

# Function to process the uploaded PDF and extract the first page as an image
def process_pdf_upload(uploaded_file):
    if uploaded_file is not None:
        # Convert PDF to images
        pdf_images = pdf2image.convert_from_bytes(uploaded_file.read())

        # Extract the first page of the PDF
        first_page_image = pdf_images[0]

        # Convert the first page image to bytes
        image_byte_array = io.BytesIO()
        first_page_image.save(image_byte_array, format='JPEG')
        image_data = image_byte_array.getvalue()

        # Encode the image data in base64
        pdf_content = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_data).decode()
            }
        ]
        return pdf_content
    else:
        raise FileNotFoundError("No PDF file was uploaded.")

# Streamlit web application setup
st.set_page_config(page_title="AI ATS")
st.header("AI Resume ATS")

# Input fields for job description and resume upload
job_description = st.text_area("Provide Job Description: ", key="input")
uploaded_resume = st.file_uploader("Upload your resume 📄", type=["pdf"])

if uploaded_resume is not None:
    st.write("Resume PDF uploaded successfully!")

# Define prompts for different analysis tasks
resume_evaluation_prompt = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please provide a professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

match_percentage_prompt = """
You are a skilled ATS (Applicant Tracking System) scanner with expertise in data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Provide a percentage match if the resume aligns with the job description. 
Include the match percentage first, followed by missing keywords, and finally, your overall thoughts.
"""

# Streamlit button handlers
if st.button("Review the Resume"):
    if uploaded_resume is not None:
        resume_content = process_pdf_upload(uploaded_resume)
        evaluation_response = generate_gemini_response(job_description, resume_content, resume_evaluation_prompt)
        st.subheader("Resume Evaluation Response")
        st.write(evaluation_response)
    else:
        st.write("Please upload your resume.")

elif st.button("Percentage Match "):
    if uploaded_resume is not None:
        resume_content = process_pdf_upload(uploaded_resume)
        match_response = generate_gemini_response(job_description, resume_content, match_percentage_prompt)
        st.subheader("Percentage Match Response")
        st.write(match_response)
    else:
        st.write("Please upload your resume.")
