import requests

def parse_resume_affinda(file_path):
    url =  "https://api.affinda.com/v2/resumes"  # ✅ Correct API endpoint
    headers = {
        "Authorization": "Bearer aff_3370424bea151b9ea57f50387f575ad14cd18d23",  # ✅ Replace with your actual Affinda API key
    }
    files = {"file": open("Resume_Latchumi_Raman_R.pdf", "rb")}  # ✅ Ensure correct file format (.pdf, .docx)

    response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()  # ✅ Successfully parsed resume data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# Example usage
resume_data = parse_resume_affinda("/Resume_Latchumi_Raman_R.pdf")
print(resume_data)


def preprocess_resume_data(resume_data):
    """Preprocess parsed resume data from Affinda and structure key details."""

    data = resume_data.get('data', {})

    # Personal Info
    name = data.get('name', {})
    full_name = f"{name.get('first', '')} {name.get('last', '')}".strip()

    email = data.get('emails', [None])[0]
    if email:
        email = email.replace('%7c', '')

    phone_numbers = data.get('phoneNumbers', [])
    phone = phone_numbers[0] if phone_numbers else None

    # Certifications
    raw_certs = data.get('certifications', [])
    certifications = [{"certification": cert.strip()} for cert in raw_certs if cert.strip()]

    # Education
    education = [
        {
            "institution": edu.get("organization", ""),
            "degree": edu.get("accreditation", {}).get("education", ""),
            "location": (edu.get("location") or {}).get("formatted", ""),
            "start_date": (edu.get("dates") or {}).get("startDate", ""),
            "completion_date": (edu.get("dates") or {}).get("completionDate", ""),
            "grade": (edu.get("grade") or {}).get("value", ""),
        }
        for edu in data.get("education", [])
    ]

    # Work Experience Extraction
    experiences = []
    for exp in data.get("workExperiences", []):  # Direct extraction from workExperiences key
        experiences.append({
            "role": exp.get("jobTitle", "").strip(),
            "company": exp.get("organization", "").strip(),
            "location": (exp.get("location") or {}).get("formatted", ""),
            "start_date": (exp.get("dates") or {}).get("startDate", ""),
            "end_date": (exp.get("dates") or {}).get("completionDate", ""),
            "details": [desc.strip() for desc in (exp.get("jobDescription", "") or "").split("\n") if desc.strip()]
        })

    # Projects Extraction (Checking Multiple Sections)
    projects = []
    if "projects" in data:  # If Affinda provides projects in a dedicated key
        for proj in data.get("projects", []):
            projects.append({
                "title": proj.get("name", "").strip(),
                "description": proj.get("details", "").strip(),
            })

    # If projects are inside the sections list
    if not projects:
        for section in data.get("sections", []):
            if section.get("sectionType") == "Projects":
                raw_projects = section.get("text", "").split("\n")
                current_project = None
                for line in raw_projects:
                    if line.strip() and not line.strip().isdigit():  # Filter unwanted text
                        if "➢" in line or any(keyword in line.lower() for keyword in ["project", "app", "bot", "classification"]):
                            if current_project:
                                projects.append(current_project)
                            current_project = {"title": line.replace("➢", "").strip(), "description": []}
                        elif current_project:
                            current_project["description"].append(line.strip())
                if current_project:
                    projects.append(current_project)

    # Skills Extraction
    skills = list(set(skill.get("name", "").strip() for skill in data.get("skills", []) if skill.get("name", "").strip()))
    skills = [{"skill": skill} for skill in skills]

    # Final Processed Resume Data
    processed_data = {
        "personal_info": {
            "name": full_name,
            "email": email,
            "phone": phone,
        },
        "education": education,
        "work_experience": experiences,
        "projects": projects,
        "skills": skills,
        "certifications": certifications,
        "activities": []
    }

    return processed_data["skills"]
resume_skills = preprocess_resume_data(resume_data)


import pdfplumber
import re
import spacy

# Load spaCy NLP model for skill extraction
nlp = spacy.load("en_core_web_sm")

# 🔹 Expanded Predefined Skill List
COMMON_SKILLS = [
    # 🔹 Programming & IT
    "Python", "Java", "JavaScript", "C++", "C", "Go", "Rust", "Swift", "Kotlin",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Artificial Intelligence",
    "TensorFlow", "PyTorch", "Scikit-learn", "OpenCV", "Transformers",
    "Keras", "Reinforcement Learning", "Hugging Face", "XGBoost",
    "Data Science", "Data Analysis", "Big Data", "Pandas", "NumPy",
    "Matplotlib", "Seaborn", "Spark", "Hadoop", "Apache Kafka",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
    "CI/CD", "Jenkins", "DevOps", "Cloud Computing",
    "Django", "Flask", "FastAPI", "React", "Angular", "Node.js",
    "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis",
    "Cybersecurity", "Penetration Testing", "Ethical Hacking",
    "Git", "GitHub", "Jira", "Agile", "Scrum", "System Design", "Software Development",

    # 🔹 Business & Finance (B.Com, MBA, etc.)
    "Accounting", "Auditing", "Financial Analysis", "Taxation", "Bookkeeping",
    "Business Strategy", "Corporate Finance", "Investment Banking", "Financial Modeling",
    "Economics", "Risk Management", "Wealth Management", "Equity Research",
    "Cost Accounting", "Management Accounting", "Stock Market Analysis",
    "Marketing", "Digital Marketing", "SEO", "Social Media Marketing",
    "Market Research", "Brand Management", "Content Marketing",
    "Sales", "Lead Generation", "Customer Relationship Management (CRM)",
    "Human Resources", "Recruitment", "Payroll Management", "Performance Management",
    "Operations Management", "Supply Chain Management", "Procurement",
    "Entrepreneurship", "E-Commerce", "Business Analytics",

    # 🔹 Science & Research (B.Sc., M.Sc., PhD)
    "Physics", "Quantum Mechanics", "Electromagnetism", "Thermodynamics",
    "Chemistry", "Organic Chemistry", "Inorganic Chemistry", "Analytical Chemistry",
    "Biology", "Molecular Biology", "Genetics", "Microbiology", "Biotechnology",
    "Environmental Science", "Geology", "Astronomy", "Bioinformatics",
    "Mathematics", "Statistics", "Probability Theory", "Linear Algebra",
    "Operations Research", "Actuarial Science", "Data Mining",

    # 🔹 Healthcare & Life Sciences
    "Medicine", "Nursing", "Pharmacy", "Biochemistry",
    "Medical Coding", "Clinical Research", "Epidemiology",
    "Healthcare Administration", "Nutrition", "Dietetics",
    "Public Health", "Medical Imaging", "Genomics",

    # 🔹 Arts, Humanities & Communication
    "English Literature", "Creative Writing", "Journalism",
    "Public Relations (PR)", "Media Studies", "Linguistics",
    "Translation", "Content Writing", "Copywriting",
    "Editing", "Technical Writing", "Screenwriting",
    "Psychology", "Sociology", "Philosophy", "Political Science",
    "History", "Cultural Studies", "International Relations",
    "Education", "Teaching", "Instructional Design",

    # 🔹 Design, Media & Creativity
    "Graphic Design", "Adobe Photoshop", "Adobe Illustrator", "Canva",
    "UI/UX Design", "Figma", "Sketch", "User Research",
    "3D Modeling", "Animation", "Video Editing", "Final Cut Pro",
    "Photography", "Cinematography", "Sound Editing",
    "Interior Design", "Fashion Design", "Industrial Design",

    # 🔹 Soft Skills & General Competencies
    "Communication", "Public Speaking", "Presentation Skills",
    "Leadership", "Team Management", "Negotiation",
    "Time Management", "Problem-Solving", "Critical Thinking",
    "Adaptability", "Decision Making", "Project Management",
    "Customer Service", "Emotional Intelligence", "Networking",
    "Conflict Resolution", "Teamwork", "Resilience"

]

def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text

def extract_job_details(jd_text):
    """Extract job title, company, and job type from JD text."""
    job_title_match = re.search(r"Job Title:\s*(.*)", jd_text)
    company_match = re.search(r"Company:\s*(.*)", jd_text)
    job_type_match = re.search(r"Job Type:\s*(.*)", jd_text)

    job_title = job_title_match.group(1).strip() if job_title_match else "Unknown"
    company = company_match.group(1).strip() if company_match else "Unknown"
    job_type = job_type_match.group(1).strip() if job_type_match else "Unknown"

    description_start = jd_text.find("Job Description:")
    description = jd_text[description_start:].replace("Job Description:", "").strip() if description_start != -1 else ""

    return {
        "job_title": job_title,
        "company": company,
        "job_type": job_type,
        "description": description
    }

def extract_skills_from_text(text):
    """Extracts relevant skills from JD text using NLP + keyword matching."""
    doc = nlp(text.lower())  # Convert text to lowercase for consistency

    # Extract named entities related to skills
    nlp_skills = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "LANGUAGE"]]

    # Extract skills using keyword matching
    keyword_skills = [skill for skill in COMMON_SKILLS if skill.lower() in text.lower()]

    # Merge both lists and remove duplicates
    extracted_skills = list(set(nlp_skills + keyword_skills))

    return extracted_skills

def preprocess_jd(pdf_path):
    """Extract and preprocess JD details from a PDF file."""
    jd_text = extract_text_from_pdf(pdf_path)
    job_details = extract_job_details(jd_text)

    # Extract skills from description
    job_details["skills"] = extract_skills_from_text(job_details["description"])

    return job_details,job_details["skills"]

# 🔹 Run Extraction & Preprocessing
pdf_path = "Job Title.pdf"  # Use the uploaded file path
processed_jd = preprocess_jd(pdf_path)

# 🔹 Print Cleaned Output
print("✅ Processed JD Data:")
print(processed_jd)
jd_skills = processed_jd[1]
print(jd_skills)



jd_skills_str = ", ".join(jd_skills)


resume_skills = ", ".join(skill["skill"] for skill in resume_skills)


resume_skills = resume_skills.split(", ")

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

def normalize_skill(skill):
    """Removes extra descriptors like '(Programming Language)' and converts to lowercase."""
    return re.sub(r"\s*\(.*?\)", "", skill).strip()

def skill_matching_pipeline(resume_skills, jd_skills):
    """Compares Resume Skills with JD Skills using TF-IDF and BERT."""

    if not resume_skills or not jd_skills:
        print("❌ Error: Resume or JD skills are empty.")
        return {"tfidf_score": 0, "bert_score": 0, "missing_skills": []}

    # 🔹 Normalize Skills
    normalized_resume_skills = [normalize_skill(skill) for skill in resume_skills]
    normalized_jd_skills = [normalize_skill(skill) for skill in jd_skills]

    # Convert list of skills into a single string
    resume_text = " ".join(normalized_resume_skills)
    jd_text = " ".join(normalized_jd_skills)

    # 🔹 Compute TF-IDF Similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text]).toarray()  # Convert sparse matrix to array
    tfidf_score = cosine_similarity(tfidf_matrix[0].reshape(1, -1), tfidf_matrix[1].reshape(1, -1))[0][0]

    # 🔹 Compute BERT Similarity
    model = SentenceTransformer('all-MiniLM-L6-v2')
    resume_embedding = model.encode([resume_text])
    jd_embedding = model.encode([jd_text])
    bert_score = cosine_similarity(np.array(resume_embedding).reshape(1, -1), np.array(jd_embedding).reshape(1, -1))[0][0]

    # 🔹 Find Missing Skills (After Normalization)
    missing_skills = list(set(normalized_jd_skills) - set(normalized_resume_skills))

    # 🔹 Print Results in Clean Format
    print("✅ Skill Matching Results:")
    print(f"🔹 Resume Skills: {normalized_resume_skills}")
    print(f"🔹 JD Skills: {normalized_jd_skills}")
    print(f"🔹 TF-IDF Similarity Score: {round(tfidf_score, 2)}")
    print(f"🔹 BERT Similarity Score: {round(bert_score, 2)}")
    print(f"🔹 Missing Skills: {missing_skills}")

    return {
        "tfidf_score": round(tfidf_score, 2),
        "bert_score": round(bert_score, 2),
        "missing_skills": missing_skills
    }

# 🔹 Run Matching
results = skill_matching_pipeline(resume_skills, jd_skills)


# Extract missing skills from the results dictionary
missing_skills = results["missing_skills"]


import google.generativeai as genai

# Replace with your actual Gemini API key
GEMINI_API_KEY = "AIzaSyAO9jmF4t1twOuIvwRQGNDjbzwrzXdxLoo"

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)


def suggest_improvements_with_gemini(missing_skills):
    """Uses Google's Gemini API to generate personalized skill improvement suggestions."""

    if not missing_skills:
        print("✅ No missing skills. You're fully qualified!")
        return

    # Convert missing skills into a readable format
    skills_text = ", ".join(missing_skills)

    # Define the prompt for Gemini
    prompt = f"""
    I am missing the following skills: {skills_text}.
    Suggest learning resources (like courses, tutorials, and documentation) and project ideas to help me improve these skills.
    Provide structured output with two sections:
    1. Learning Resources
    2. Project Ideas
    Keep it brief and useful.
    """

    # Call Gemini API
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    # Extract and print suggestions
    print("✅ Suggested Improvements:")
    print(response.text)

# 🔹 Run Function with Missing Skills

suggest_improvements_with_gemini(missing_skills)