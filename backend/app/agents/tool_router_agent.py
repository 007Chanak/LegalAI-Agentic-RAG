from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

AVAILABLE_TOOLS = [

    "termination_clause_tool",

    "payment_clause_tool",

    "liability_clause_tool",

    "none"
]

def route_tools(question):

    prompt = f"""
    You are a tool routing agent.

    Your task is to determine
    which tool is MOST appropriate
    for the user's question.

    Available tools:

    termination_clause_tool
    payment_clause_tool
    liability_clause_tool
    none

    Return ONLY a comma-separated listof tool names.

    Example:
    payment_clause_tool, liability_clause_tool

    If no tools needed:
    none

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

    tools = (
        response
        .choices[0]
        .message
        .content
        .strip()
        .lower()
    )

    selected_tools = [

        tool.strip()

        for tool in tools.split(",")

        if tool.strip() in AVAILABLE_TOOLS
    ]

    if not selected_tools:

        return ["none"]

    return selected_tools