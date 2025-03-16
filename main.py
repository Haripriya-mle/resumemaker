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
from typing import Optional

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
    experience: str
    skills: str
    education: str
    certifications: str
    job_description: str
    projects: str
    cover_letter: Optional[str] = None 

@app.post("/generate_resume/")
def generate_resume(data: ResumeRequest):
    """
    Generates an ATS-friendly resume as a dictionary response.
    """

    # 1. Generate ATS-Optimized Professional Summary
    summary_prompt = f"""
    Based on this job description:
    {data.job_description}
    
    Generate a concise, ATS-optimized professional summary in 30 words using the candidate's details:
    {data.experience}, {data.skills}, {data.education}, {data.certifications}.
    
    Prioritize keywords and skills mentioned in the job description.
    Do NOT include any headings like 'Professional Summary' or 'Summary'.
    Return only the summary content.
    """

    summary_response = agent.run(summary_prompt)
    summary = summary_response.content.strip()

    # 2. Filter Relevant Skills
 
    skills_prompt = f"""
    Job Description:
    {data.job_description}
    
    Candidate's Extracted Skills:
    {data.skills}
    
    From the candidate's skills, filter out only the most relevant ones for the job.
    Prioritize technical skills, industry-standard terms, and essential keywords important for ATS.
    Exclude any soft skills or unrelated skills.
    
    - Do NOT include any headings like 'Relevant Skills'.
    - Return the final list of relevant skills in a concise, comma-separated format without extra descriptions.
    
    Return the filtered skills.
    """


    skills_response = agent.run(skills_prompt)
    filtered_skills = skills_response.content.strip()
    

    # 3. Filter Relevant Experience

   
    experience_prompt = f"""
    Job Description:
    {data.job_description}
    
    Candidate's Experience:
    {data.experience}    
    Extract the most relevant experiences based on the job description. 
    Prioritize achievements, responsibilities, and keywords that align with the job description. 
    Ensure the following formatting and clarity guidelines:
    
    - **Each job entry should include**:
      - Job Title | Company Name | Location (if available)
      - Duration (Month/Year – Month/Year or Present)
      - A concise set of bullet points highlighting key achievements and responsibilities.
    - Use structured bullet points (without *, +, or any other symbols).  
    - Start each bullet point with an action verb (e.g., Developed, Designed, Built).  
    - If multiple entries share the same time period, keep only one instance of the date.  
    - Ensure each experience is separated into paragraphs with proper punctuation.  
    - Do NOT include section headings like 'Relevant Experience' or 'Experience'.  
    - Exclude any concluding notes, summaries, or personal analysis.  
    
    Return the formatted experience in the following structure:  
    
    Python Developer | Self-Learning & Projects | [City, Country]  
    June 2022 – Present  
    • Mastered Python with a focus on data analysis, web development, and machine learning.  
    • Completed an intensive Django course to build dynamic web applications.  
    • Developed expertise in data visualization, statistical modeling, and predictive analytics.  
    • Explored AI concepts including computer vision and reinforcement learning.  
    • Implemented deep learning models for image classification and NLP.  
    
    Full-Stack Developer | E-commerce & Web Applications | [City, Country]  
    March 2020 – June 2022  
    • Built Magento e-commerce applications for flower shops and restaurants.  
    • Designed and developed websites for real estate agencies and networking equipment shops.  
    • Conducted unit testing, reducing defects and improving customer satisfaction.  
    • Created and updated instructional documentation and trained interns.  
    • Developed software applications, utilizing PHP and MySQL.  
    • Designed and deployed websites with cross-device compatibility.  
 
    
    Return only the structured experience in this exact format.
    """


    experience_response = agent.run(experience_prompt)
    filtered_experience = experience_response.content.strip()

    # 4. Filter Relevant Education

    education_prompt = f"""
    Job Description:
    {data.job_description}
    
    Candidate's Education:
    {data.education}
    
    Extract and format the most relevant degree based on the job description.
    Ensure a concise and professional presentation.
    
    - **Return only the most relevant degree** that aligns with the job role.
    - **Include the field of study and institution name** for clarity.
    - **no  Summary or details.**
    - **Exclude secondary or less relevant degrees unless specifically required.**
    - **Do NOT include section headings such as 'Education' or 'Relevant Education'.**
    - **Avoid bullet points, markdown, or unnecessary details.**
    
    Return the formatted education in the following structure:
    Bachelor of Technology in Computer Science and Engineering  
    Sree Narayana Gurukulam College of Engineering, Kollenchery (2011 – 2015)  

    """
    

    education_response = agent.run(education_prompt)
    filtered_education = education_response.content.strip()

    # 5. Filter Relevant Certifications

    certifications_prompt = f"""
    Job Description:
    {data.job_description}
    
    Candidate's Certifications:
    {data.certifications}
    
    Extract the most relevant certifications based on the job description.
    Prioritize certifications that are directly mentioned or implied in the job description.
      
    - Do NOT include headings like 'Certifications' or 'Relevant Certifications'.
    - Do NOT use bullet points (*, +) or any other symbols.
    - If no relevant certifications exist, return "None".
    - Do NOT include any unnecessary explanations—just return the filtered certifications.
    Return the formatted certifications in the following structure:

    Machine Learning Specialization – Coursera  
    Deep Learning Specialization – Coursera  
    Natural Language Processing (NLP) – Coursera  
    Generative Adversarial Networks (GAN) – Coursera  
    """
    certifications_response = agent.run(certifications_prompt)
    filtered_certifications = certifications_response.content.strip()
    if "None" in filtered_certifications or not filtered_certifications:
        filtered_certifications = None
   
    projects_prompt = f"""
    Job Description:
    {data.job_description}
    
    Candidate's Projects:
    {data.projects}
    
    Extract and format the most relevant projects based on the job description.
    Follow these formatting guidelines:
    
    - **Start each project with its title** (avoid numbering or section headings).
    - **Include the technologies used in a concise manner** after the project title.
    - **Use structured bullet points** for achievements (without symbols like *, +, or -).
    - **Maintain proper paragraph spacing** for readability.
    - **Do NOT include generic section headings** like 'Projects' or 'Relevant Projects'.
    - **Ensure no markdown formatting**, just clean professional text.
     If no relevant projects exist, return "None".
     if only single one return that
    - Do NOT include any unnecessary explanations—just return the filtered projecct.
    Do NOT include a 'Projects' heading.
    **Return the formatted projects in this structure:**
    
    AI-Powered Resume & Cover Letter Generator  
    Technologies used: Python, FastAPI, GPT  
    • Built an ATS-friendly resume generator that tailors experiences based on job descriptions.  
    • Implemented GPT-based filtering for relevant skills, experience, and education.  
    • Designed a seamless HTML-based resume export for easy PDF downloads.  
    GitHub: [GitHub Link]
    
    E-Commerce Customization Agent  
    Technologies used: Magento, Python, AI  
    • Developed an AI-powered assistant to personalize customer shopping experiences.  
    • Integrated recommendation algorithms to increase conversion rates.  
    GitHub: [GitHub Link]
    
    Return the formatted projects exactly as shown in the example above.
    """

    projects_response = agent.run(projects_prompt)
    filtered_projects = projects_response.content.strip()
    # 6. Create ATS-Optimized Cover Letter
    cover_letter_prompt = f"""
    Job Description:
    {data.job_description}

    Candidate's Summary:
    {summary}

    Candidate's Relevant Skills:
    {filtered_skills}

    Candidate's Relevant Experience:
    {filtered_experience}

    Generate a concise and ATS-optimized cover letter based on the above information.
    Highlight key skills, achievements, and motivations for applying to this position.
    """
    cover_letter_response = agent.run(cover_letter_prompt)
    cover_letter = cover_letter_response.content.strip()
     # Function to clean and format text
    def clean_text(text):
        """Removes markdown-style formatting like *, ###, and excessive whitespace while keeping punctuation."""
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # Remove bold (**text** → text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)      # Remove bullet points (*text* → text)
        text = re.sub(r"###\s*", "", text)             # Remove headings (### text → text)
        text = re.sub(r"\s*\n\s*", "\n", text.strip())  # Normalize spacing
        return text

    # Apply cleaning function
    cleaned_summary = clean_text(summary)
    cleaned_skills = clean_text(filtered_skills)
    cleaned_education = clean_text(filtered_education)
    cleaned_cover_letter = clean_text(cover_letter) if cover_letter else None
    
    resume_data = {
        "name": data.name,
        "phone": data.phone,
        "email": data.email,
        "linkedin": data.linkedin,
        "website": data.website,
        "summary": cleaned_summary,
        "projects":filtered_projects,
        "experience": filtered_experience,
        "skills": cleaned_skills,
        "education": cleaned_education,
        "certifications": filtered_certifications,  # Assuming no special formatting needed
        "cover_letter": cleaned_cover_letter
    }
    
    return {"resume": resume_data}

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
        name_match = re.search(r"^([A-Z][a-zA-Z]*(?: [A-Z][a-zA-Z]*)*)", text)
        phone_match = re.search(r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        linkedin_match = re.search(r"https?:\/\/(www\.)?linkedin\.com\/(in|profile)\/[A-Za-z0-9-_%]+", text)
        website_match = re.search(r"https?:\/\/(?!www\.linkedin\.com\/)[A-Za-z0-9.-]+\.[a-z]{2,}(\/\S*)?", text)

        experience_match = re.search(r"(?i)Experience\n(.*?)(?=Education|Skills|Projects|$)", text, re.DOTALL)
        skills_match = re.search(r"(?i)Skills\n(.*?)(?=Education|Experience|Projects|$)", text, re.DOTALL)
        projects_match = re.search(r"(?i)Projects\n(.*?)(?=Education|Experience|Projects|$)", text, re.DOTALL)
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
            "projects": projects_match.group(1).strip() if projects_match else "",
            "education": education_match.group(1).strip() if education_match else "",
            "certifications": certifications_match.group(1).strip() if certifications_match else "",
        }
    print("extracffted_text",extracted_text)
    parsed_data = extract_with_regex(extracted_text)
    print("pdataaaaaaaaaaaaa",parsed_data)
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
    # Constructing the prompt
    llm_prompt = f"""
    Based on the following candidate details:
    {parsed_data}
    
    Extract the most relevant skills of the candidate, focusing on:
    - Technical skills
    - Industry-standard terms
    - Keywords important for ATS
    
    Return the skills in a comma-separated format.
    """
    
    
    # Send the prompt to the agent and get the response
    llm_response = agent.run(llm_prompt)
    
    # Store the extracted skills
    parsed_data["skills"] = llm_response.content.strip()
    
    # Check if skills were extracted
    if parsed_data["skills"] != '':
        print("Extracted Skills:", parsed_data["skills"])
    else:
        print("LLM Response:", llm_response.content.strip())
        print("Possible issue with the prompt.")
    
    print("parsedjjjjjjjjjjjjjjjjjjjjjjjjjjj_resume",parsed_data)
    return {"parsed_resume": parsed_data}

def truncate_text(text, limit=3000):
    """Truncate text if it exceeds the character limit."""
    return text[:limit] + "..." if len(text) > limit else text
