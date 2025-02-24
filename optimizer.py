import os
import google.generativeai as genai
import yaml
from helper_lib import read_text_file, write_to_text_file, getPrompt

# Load configuration from Config.yaml
try:
    with open('Config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)
except FileNotFoundError:
    print("❌ Error: Config.yaml file not found.")
    exit(1)
except yaml.YAMLError as e:
    print(f"❌ Error: An error occurred while parsing Config.yaml: {e}")
    exit(1)


# Configure Gemini API
genai.configure(api_key="AIzaSyAO9jmF4t1twOuIvwRQGNDjbzwrzXdxLoo")

# Workspace-Specific Paths
JOB_POS_FOLDER = config['JOB_POS_FOLDER']
OUTPUT_FOLDER = config['OUTPUT_FOLDER']
RESUME_PATH = config['RESUME_PATH']


# 🔹 Function to Call Gemini API
def sendLLMRequest(prompt):
    """Sends a request to Google Gemini API."""
    try:
        model = genai.GenerativeModel(LLM_MODEL)
        response = model.generate_content(prompt, generation_config={"temperature": LLM_TEMPERATURE})
        return response.text.strip() if response.text else "❌ Error: No response from Gemini API."
    except Exception as e:
        print(f"❌ An unexpected error occurred while calling Gemini API: {e}")
        return None  

# 🔹 Main Function
def main():
    """Processes resume optimization for multiple job descriptions."""
    
    # Read original resume
    md_resume = read_text_file(RESUME_PATH)
    if md_resume is None:
        print("❌ Error: Failed to read the resume.")
        return

    # List job description files
    try:
        dir_list = os.listdir(JOB_POS_FOLDER)
    except FileNotFoundError:
        print(f"❌ Error: The directory {JOB_POS_FOLDER} was not found.")
        return
    except IOError:
        print(f"❌ Error: An I/O error occurred while accessing the directory {JOB_POS_FOLDER}.")
        return
    
    print("🚀 >>> START <<<")
    for filename in dir_list:
        print(f"🔹 Processing {filename}")

        # Read job description
        job_description = read_text_file(os.path.join(JOB_POS_FOLDER, filename))
        if job_description is None:
            print(f"❌ Error: Failed to read the job description file {filename}.")
            continue  # Skip this JD and proceed to the next
        
        # Generate prompt for optimization
        prompt = getPrompt(md_resume, job_description)

        # Get optimized resume using Gemini
        optimized_resume = sendLLMRequest(prompt)
        if not optimized_resume:
            print(f"❌ Error: Failed to optimize resume for {filename}.")
            continue  # Skip to the next JD
        
        # Save optimized resume
        output_file_path = os.path.join(OUTPUT_FOLDER, f'resume-{filename}.md')
        write_to_text_file(output_file_path, optimized_resume)
        print(f"✅ Resume optimized and saved: {output_file_path}")

    print("🚀 >>> END <<<")

# 🔹 Run Script
if __name__ == "_main_":
    main()