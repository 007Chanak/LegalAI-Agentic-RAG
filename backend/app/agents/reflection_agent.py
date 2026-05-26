from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

def reflection_check(
    question,
    context
):

    prompt = f"""
    You are a retrieval evaluation agent.

    Your task is to determine whether the retrieved context
    is reasonably sufficient
    to answer the question adequately.

    Only return NO if critical information
    is clearly missing.

    Respond ONLY with:
    YES
    or
    NO

    User Question:
    {question}

    Retrieved Context:
    {context}

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

    decision = (
        response
        .choices[0]
        .message
        .content
        .strip()
        .upper()
    )

    return "YES" in decision