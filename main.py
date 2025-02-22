import ssl
from fastapi import FastAPI, File, UploadFile, Form, Response
from pydantic import BaseModel
from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv, dotenv_values
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
#import docx
import os
import io
import re
from fpdf import FPDF

# Load environment variables
load_dotenv()
config = dotenv_values(".env")

# Ensure SSL is available
try:
    ssl.create_default_context()
except AttributeError:
    raise ImportError("SSL module is not available. Please check your Python environment.")

app = FastAPI()

# Allow requests from frontend (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust this to match your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI model (Groq API)
agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    markdown=True
)

# Define request model
class ResumeRequest(BaseModel):
    name: str
    phone: str
    email: str
    linkedin: str
    website: str
    summary: str
    experience: str
    skills: str
    education: str
    certifications: str
    job_description: str
class ResumeData(BaseModel):
    name: str
    phone: str
    email: str
    linkedin: str
    website: str
    summary: str
    experience: str
    skills: str
    education: str
    certifications: str
@app.post("/generate_resume/")
def generate_resume(data: ResumeRequest):
    """
    Generates an ATS-friendly resume as a dictionary response.
    """

    prompt = f"""
    Based on this job description:
    {data.job_description}

    Generate a professional summary using the candidate's experience:
    {data.experience}
    """
    
    response = agent.run(prompt)
    summary = response.content.strip()
    if not data["skills"]:
        return ""

    llm_prompt = f"""
    Job Description:
    {data["job_description"]}

    Candidate's Extracted Skills:
    {data["skills"]}

    From the candidate's skills, filter out the most relevant ones for the job.
    Prioritize technical skills, industry-standard terms, and keywords important for ATS.
    If any essential skill from the job description is missing, suggest related ones from the candidate’s experience.

    Return the final list of relevant skills in a comma-separated format.
    """

    llm_response = agent.run(llm_prompt)
    skills= llm_response.content.strip()
    # Create structured JSON response
    resume_data = {
        "name": data.name,
        "phone":data.phone,
        "email": data.email,
        "linkedin":data.linkedin,
        "website":data.website,
        "summary": summary,
        "experience": data.experience,
        "skills": data.skills,
        "education": data.education,
        "certifications": data.certifications
    }

    return {"resume": resume_data}
@app.post("/generate_resume2/")
def generate_resume(data: ResumeRequest):
    """
    Generates an ATS-friendly resume as a dictionary response.
    """

    prompt = f"""
    Based on this job description:
    {data.job_description}

    Generate a professional summary using the candidate's experience:
    {data.experience}
    """
    
    response = agent.run(prompt)
    summary = response.content.strip()

    # Create structured JSON response
    resume_data = {
        "name": data.name,
        "summary": summary,
        "experience": data.experience,
        "skills": data.skills,
        "education": data.education
    }
    pdf = FPDF(format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()


    font_dir = os.path.abspath("dejavu-sans")
    regular_font_path = os.path.join(font_dir, "DejaVuSans.ttf")
    bold_font_path = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
    
    # Add both fonts
    pdf.add_font("DejaVu", "", regular_font_path, uni=True)
    pdf.add_font("DejaVu", "B", bold_font_path, uni=True)

   
    # 🔹 Use a Unicode font (DejaVuSans) to support all characters
    pdf.set_font("DejaVu", "", 12)

    # Header (Name)
    pdf.set_font("DejaVu", style='B', size=16)
    pdf.cell(200, 10, data.name, ln=True, align='C')
    pdf.ln(10)

    sections = [
        ("Profile Summary", summary, 3000),
        ("Work Experience", data.experience, 4000),
        ("Skills", data.skills, 1000),
        ("Education", data.education, 3000),
    ]

    for title, content, limit in sections:
        pdf.set_font("DejaVu", style='B', size=12)
        pdf.cell(200, 10, title, ln=True)
        pdf.set_font("DejaVu", size=10)

        # Adjust font size if text is too long
        if len(content) > limit * 1.2:
            pdf.set_font("DejaVu", size=9)

        pdf.multi_cell(190, 7, truncate_text(content, limit))
        pdf.ln(5)

    # Ensure proper page breaks
    if pdf.get_y() > 260:
        pdf.add_page()

    # Convert to Bytes (for API response)
    pdf_bytes = bytes(pdf.output(dest='S'))    # Get PDF as bytearray
    
    #return Response(content=pdf_bytes, media_type="application/pdf")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=resume.pdf"}  # ✅ Forces download
    )
@app.post("/parse_resume/")
def parse_resume(resume_file: UploadFile = File(...)):
    """Parses resume file and extracts structured text."""
    extracted_text = ""
    
    if resume_file.filename.endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(resume_file.file.read())) as pdf:
            extracted_text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    
    else:
        return {"error": "Unsupported file format. Please upload a PDF or DOCX."}
    # Step 2: Extract data using regex
    def extract_with_regex(text):
        """Extracts structured data using regex patterns."""
        name_match = re.search(r"^([A-Z][a-z]+(?: [A-Z][a-z]+)*)", text)
        phone_match = re.search(r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        linkedin_match = re.search(r"(https?:\/\/(www\.)?linkedin\.com\/in\/[A-Za-z0-9-_%]+)", text)
        website_match = re.search(r"(https?:\/\/[A-Za-z0-9.-]+\.[a-z]{2,})", text)

        experience_match = re.search(r"(?i)Work Experience\n(.*?)(?=Education|Skills|Projects|$)", text, re.DOTALL)
        skills_match = re.search(r"(?i)Skills\n(.*?)(?=Education|Experience|Projects|$)", text, re.DOTALL)
        education_match = re.search(r"(?i)Education\n(.*?)(?=Skills|Experience|Projects|$)", text, re.DOTALL)
        certifications_match = re.search(r"(?i)Certifications\n(.*?)(?=Skills|Education|Experience|Projects|$)", text, re.DOTALL)

        return {
            "name": name_match.group(1) if name_match else "",
            "phone": phone_match.group(0) if phone_match else "",
            "email": email_match.group(0) if email_match else "",
            "linkedin": linkedin_match.group(0) if linkedin_match else "",
            "website": website_match.group(0) if website_match else "",
            "experience": experience_match.group(1).strip() if experience_match else "",
            "skills": skills_match.group(1).strip() if skills_match else "",
            "education": education_match.group(1).strip() if education_match else "",
            "certifications": certifications_match.group(1).strip() if certifications_match else "",
        }

    parsed_data = extract_with_regex(extracted_text)

     # Step 3: LLM Cleanup for Experience, Education, Skills
    def clean_section_with_llm(section_name, section_text):
        """Uses LLM to clean and properly structure a resume section."""
        if not section_text:
            return ""

        prompt = f"""
        The following is a raw extracted {section_name} section from a resume. 
        Clean it by removing page numbers, unrelated text, and formatting it professionally:
        
        {section_text}

        Provide the cleaned {section_name} section in a structured format.
        """
        response = agent.run(prompt)
        return response.content.strip()

    parsed_data["experience"] = clean_section_with_llm("Work Experience", parsed_data["experience"])
    parsed_data["education"] = clean_section_with_llm("Education", parsed_data["education"])
    parsed_data["skills"] = clean_section_with_llm("Skills", parsed_data["skills"])

    # Step 4: If experience is missing, return an error
    if not parsed_data["experience"]:
        return {"error": "Experience section not found in the resume. Please upload a valid file."}

    # Step 5: LLM to generate a summary based on experience
    llm_prompt = f"""
    Based on this job experience:
    {parsed_data["experience"]}

    Generate a professional summary highlighting key achievements and skills.
    """
    llm_response = agent.run(llm_prompt)
    parsed_data["summary"] = llm_response.content.strip()

    return {"parsed_resume": parsed_data}

def truncate_text(text, limit=3000):
    """Truncate text if it exceeds the character limit."""
    return text[:limit] + "..." if len(text) > limit else text
