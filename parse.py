import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
import io

app = Flask(__name__)

AFFINDA_API_KEY = "aff_87914e1798fceefa12c9e4aaaede03e2688b48ab"
AFFINDA_URL = "https://api.affinda.com/v2/resumes"
HEADERS = {"Authorization": f"Bearer {AFFINDA_API_KEY}"}

# Connect to MongoDB
client = MongoClient("mongodb+srv://wengaboy:mypassword@firstmongoproj.5guew.mongodb.net/hackathon")
db = client["ResumeDatabase"]
users_col = db["Users"]

@app.route("/upload", methods=["POST"])
def process_resume():
    try:
        file_data = request.data  # Get binary file data
        if not file_data:
            return jsonify({"error": "No file received"}), 400

        # Convert binary data into a file-like object
        pdf_file = io.BytesIO(file_data)

        # Send file to Affinda API
        files = {"file": ("resume.pdf", pdf_file, "application/pdf")}
        response = requests.post(AFFINDA_URL, headers=HEADERS, files=files)

        # Check if Affinda processed the resume successfully
        if response.status_code != 200:
            return jsonify({"error": "Affinda API failed", "details": response.text}), 500

        parsed_data = response.json()
        print(parsed_data)

        # 🔹 Check if 'data' exists and is valid
        if "data" not in parsed_data or parsed_data["data"] is None:
            return jsonify({"error": "Invalid response from Affinda API", "details": parsed_data}), 500

        # 🔹 Check if 'error' key exists and has values
        if "error" in parsed_data and parsed_data["error"] is not None:
            error_details = parsed_data["error"]

        if error_details.get("errorCode") or error_details.get("errorDetail"):
                return jsonify({"error": "Affinda API returned an error", "details": error_details}), 500

        # Process and structure the extracted data
        structured_resume_data = preprocess_resume_data(parsed_data)

        # Insert data into MongoDB and get the user ID
        user_id = insert_into_mongodb(structured_resume_data)

        return jsonify({"message": "Resume processed successfully", "user_id": str(user_id)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


import re

def preprocess_resume_data(affinda_data):
    """
    Processes the parsed resume data from Affinda API, 
    handling missing fields and structuring the data properly.
    """

    data = affinda_data.get("data", {})

    # 🔹 Helper function to safely extract nested values
    def safe_get(obj, keys, default="N/A"):
        for key in keys:
            if isinstance(obj, dict):
                obj = obj.get(key, default)
            else:
                return default
        return obj if obj else default

    # 🔹 Extracting Basic Information
    name = f"{safe_get(data, ['name', 'first'])} {safe_get(data, ['name', 'last'])}".strip()
    email = safe_get(data, ["emails", 0])
    phone = safe_get(data, ["phoneNumbers", 0])

    # ✅ Cleaning Email (fixes issue with '%7c' encoding)
    email = email.replace("%7c", "") if email != "N/A" else "N/A"

    # 🔹 Extracting Certifications
    raw_certs = data.get("certifications", [])
    certifications = [{"certification": cert.strip()} for cert in raw_certs if cert.strip()]

    # 🔹 Extracting Education
    education = [
        {
            "institution": safe_get(edu, ["organization"]),
            "degree": safe_get(edu, ["accreditation", "education"]),
            "location": safe_get(edu, ["location", "formatted"]),
            "start_date": safe_get(edu, ["dates", "startDate"]),
            "completion_date": safe_get(edu, ["dates", "completionDate"]),
            "grade": safe_get(edu, ["grade", "value"]),
        }
        for edu in data.get("education", []) if edu
    ]

    # 🔹 Extracting Work Experience (Handles multiple roles in the same company)
    experiences = []
    for section in data.get("sections", []):
        if section.get("sectionType") == "WorkExperience":
            raw_experience = section.get("text", "").split("\n")
            current_exp = None
            for line in raw_experience:
                if any(role in line for role in ["Intern", "Engineer", "Developer", "Researcher"]):
                    if current_exp:
                        experiences.append(current_exp)
                    current_exp = {"role": line.strip(), "details": []}
                elif current_exp:
                    current_exp["details"].append(line.strip())
            if current_exp:
                experiences.append(current_exp)

    # 🔹 Extracting Projects
    projects = []
    for section in data.get("sections", []):
        if section.get("sectionType") == "Projects":
            raw_projects = section.get("text", "").split("\n")
            current_project = None
            for line in raw_projects:
                if "➢" in line:
                    if current_project:
                        projects.append(current_project)
                    current_project = {"title": line.replace("➢", "").strip(), "description": []}
                elif current_project:
                    current_project["description"].append(line.strip())
            if current_project:
                projects.append(current_project)

    # 🔹 Extracting Skills (Avoids duplicates)
    skills = list(set(skill.get("name", "N/A") for skill in data.get("skills", [])))
    skills = [{"skill": skill} for skill in skills if skill != "N/A"]

    # 🔹 Final Processed Data
    processed_data = {
        "personal_info": {
            "name": name if name else "Unknown",
            "email": email,
            "phone": phone if phone != "N/A" else "N/A",
        },
        "education": education if education else [{"institution": "N/A", "degree": "N/A"}],
        "work_experience": experiences if experiences else [{"role": "N/A", "details": ["No experience listed"]}],
        "projects": projects if projects else [{"title": "N/A", "description": ["No projects listed"]}],
        "skills": skills if skills else [{"skill": "No skills listed"}],
        "certifications": certifications if certifications else [{"certification": "No certifications listed"}],
        "activities": []  # Placeholder for future data
    }

    return processed_data




def insert_into_mongodb(data):
    """Inserts processed resume data into MongoDB and returns the inserted user ID."""
    user_id = users_col.insert_one(data).inserted_id
    return user_id


if __name__ == "__main__":
    app.run(port=5001, debug=True)
