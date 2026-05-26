from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

def summarize_memory(history):

    conversation = ""

    for msg in history:

        role = msg.get(
            "role",
            "user"
        )

        content = msg.get(
            "content",
            ""
        )

        conversation += (
            f"{role}: {content}\n"
        )

    prompt = f"""
    Summarize the important parts
    of this conversation.

    Focus on:
    - important legal discussion
    - user intent
    - referenced documents
    - conclusions
    - ongoing context

    Keep summary concise.

    Conversation:
    {conversation}
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