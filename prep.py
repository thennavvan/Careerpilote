from fastapi import FastAPI
from pydantic import BaseModel
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# Configure Gemini API Key
genai.configure(api_key="AIzaSyAwLh4fuDUPitPYuht0WVSZlYUkxlm1vqg")

app = FastAPI()

# Allow frontend to make requests to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: list
    state: dict

SYSTEM_PROMPT = """
You are a Job Interview Preparation Bot. You generate interview questions based on job descriptions provided by the user.
For each question, you also generate a sample answer. Your response should be formatted in Markdown for readability.
"""

def generate_interview_questions_and_answers(job_description):
    """Generates a list of interview questions and their corresponding answers."""
    
    prompt = f"""
    Based on the following job description, generate interview questions. 
    Then, immediately provide a sample answer for each question.

    Job Description: {job_description}
    """
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    return response.text.strip()

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_message = request.messages[-1]["content"].strip()
    state = request.state

    if "phase" not in state:
        state["phase"] = "job_description"

    if state["phase"] == "job_description":
        state["job_description"] = user_message
        qa_content = generate_interview_questions_and_answers(user_message)

        bot_response = {
            "content": f"*Here are your interview questions and sample answers:*\n\n{qa_content}",
            "role": "assistant"
        }
        state["phase"] = "feedback"

    elif state["phase"] == "feedback":
        model = genai.GenerativeModel("gemini-1.5-flash")
        feedback_prompt = f"{SYSTEM_PROMPT}\nUser Response: {user_message}\nProvide feedback on the user's interview responses."
        response = model.generate_content(feedback_prompt)

        bot_response = {
            "content": "*Feedback:*\n\n" + response.text,
            "role": "assistant"
        }

    return {"botResponse": bot_response, "newState": state}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
