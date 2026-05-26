from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

def create_workflow_plan(question):

    prompt = f"""
    You are an AI workflow planner.

    Create a concise execution plan
    for answering the user's legal query.

    Available capabilities:
    - document retrieval
    - clause extraction
    - legal analysis
    - comparison
    - summarization

    Return ONLY the numbered plan.

    User Question:
    {question}
    """

    response = (
        groq_client.chat.completions.create(

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            model="llama-3.1-8b-instant"
        )
    )

    return (
        response
        .choices[0]
        .message
        .content
    )