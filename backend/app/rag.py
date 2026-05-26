from pinecone import Pinecone
from dotenv import load_dotenv

import os
import time
import uuid

from groq import Groq

import pdfplumber
from PyPDF2 import PdfReader

from app.planners.query_planner import (
    plan_query
)

from app.agents.reflection_agent import (
    reflection_check
)

from app.tools.clause_extraction_tool import (
    extract_clause_tool
)

from app.agents.tool_router_agent import (
    route_tools
)

from app.memory.memory_agent import (
    summarize_memory
)

from app.workflows.workflow_planner import (
    create_workflow_plan
)

load_dotenv()

# -------------------------------
# PINECONE SETUP
# -------------------------------

pc = Pinecone(
    api_key=os.getenv(
        "PINECONE_API_KEY"
    )
)

index = pc.Index(
    os.getenv(
        "PINECONE_INDEX"
    )
)

# -------------------------------
# GROQ CLIENT
# -------------------------------

groq_client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

print(
    "GROQ KEY EXISTS:",
    bool(os.getenv("GROQ_API_KEY"))
)

# -------------------------------
# TEXT CHUNKER
# -------------------------------

def split_text(
    text,
    chunk_size=1200,
    overlap=150
):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += (
            chunk_size - overlap
        )

    return chunks


# -------------------------------
# CREATE EMBEDDING
# -------------------------------

def create_embedding(
    text,
    input_type="passage"
):

    embedding = pc.inference.embed(

        model="multilingual-e5-large",

        inputs=[text],

        parameters={
            "input_type": input_type,
            "truncate": "END"
        }
    )

    return embedding[0]["values"]


# -------------------------------
# PDFPLUMBER EXTRACTOR
# -------------------------------

def extract_with_pdfplumber(file_path):

    documents = []

    try:

        with pdfplumber.open(file_path) as pdf:

            print(
                "PDFPLUMBER TOTAL PAGES:",
                len(pdf.pages)
            )

            for i, page in enumerate(pdf.pages):

                try:

                    text = page.extract_text()

                    if not text:
                        text = ""

                    text = text.strip()

                    print(
                        f"PDFPLUMBER PAGE {i+1} LENGTH:",
                        len(text)
                    )

                    if len(text) > 20:

                        documents.append({

                            "page":
                            i + 1,

                            "text":
                            text
                        })

                except Exception as e:

                    print(
                        f"PDFPLUMBER PAGE ERROR:",
                        str(e)
                    )

    except Exception as e:

        print(
            "PDFPLUMBER ERROR:",
            str(e)
        )

    return documents


# -------------------------------
# PYPDF2 FALLBACK
# -------------------------------

def extract_with_pypdf2(file_path):

    documents = []

    try:

        reader = PdfReader(file_path)

        print(
            "PYPDF2 TOTAL PAGES:",
            len(reader.pages)
        )

        for i, page in enumerate(reader.pages):

            try:

                text = page.extract_text()

                if not text:
                    text = ""

                text = text.strip()

                print(
                    f"PYPDF2 PAGE {i+1} LENGTH:",
                    len(text)
                )

                if len(text) > 20:

                    documents.append({

                        "page":
                        i + 1,

                        "text":
                        text
                    })

            except Exception as e:

                print(
                    f"PYPDF2 PAGE ERROR:",
                    str(e)
                )

    except Exception as e:

        print(
            "PYPDF2 ERROR:",
            str(e)
        )

    return documents


# -------------------------------
# MAIN PDF EXTRACTOR
# -------------------------------

def extract_text_from_pdf(file_path):

    start_time = time.time()

    print(
        "STARTING PDF EXTRACTION"
    )

    # -------------------------------
    # TRY PDFPLUMBER
    # -------------------------------

    documents = extract_with_pdfplumber(
        file_path
    )

    # -------------------------------
    # FALLBACK TO PYPDF2
    # -------------------------------

    if len(documents) == 0:

        print(
            "TRYING PYPDF2 FALLBACK"
        )

        documents = extract_with_pypdf2(
            file_path
        )

    print(
        "DOCUMENTS EXTRACTED:",
        len(documents)
    )

    print(
        "PDF LOAD TIME:",
        time.time() - start_time
    )

    return documents


# -------------------------------
# PROCESS PDF
# -------------------------------

def process_pdf(file_path, session_id):

    start_time = time.time()

    document_id = str(uuid.uuid4())

    documents = extract_text_from_pdf(
        file_path
    )

    if len(documents) == 0:

        print(
            "NO TEXT COULD BE EXTRACTED"
        )

        return None

    # -------------------------------
    # COMBINE TEXT
    # -------------------------------

    combined_text = ""

    for doc in documents:

        combined_text += (
            doc["text"] + "\n"
        )

    print(
        "TOTAL TEXT LENGTH:",
        len(combined_text)
    )

    # -------------------------------
    # CHUNKING
    # -------------------------------

    chunks = split_text(
        combined_text
    )

    print(
        "TOTAL CHUNKS:",
        len(chunks)
    )

    # -------------------------------
    # EMBEDDINGS
    # -------------------------------

    vectors = []

    embedding_start = time.time()

    for i, chunk in enumerate(chunks):

        try:

            embedding = create_embedding(
                chunk
            )

        except Exception as e:

            print(
                "EMBEDDING ERROR:",
                str(e)
            )

            continue

        vectors.append(

            (

                f"{document_id}-chunk-{i}",

                embedding,

                {

                    "text":
                    chunk,

                    "source":
                    os.path.basename(
                        file_path
                    ),

                    "document_id":
                    document_id
                }
            )
        )

    print(
        "TOTAL VECTORS:",
        len(vectors)
    )

    print(
        "EMBEDDING TIME:",
        time.time() - embedding_start
    )

    if len(vectors) == 0:

        print(
            "NO VECTORS GENERATED"
        )

        return None

    # -------------------------------
    # PINECONE UPSERT
    # -------------------------------

    print(
        "UPSERTING FILE:",
        os.path.basename(file_path)
    )

    print(
        "SESSION ID:",
        session_id
    )

    print(
        "VECTOR COUNT:",
        len(vectors)
    )

    try:

        index.upsert(

            vectors=vectors,

            namespace=session_id
        )

    except Exception as e:

        print(
            "PINECONE UPSERT ERROR:",
            str(e)
        )

        return None

    print(
        "TOTAL PROCESS TIME:",
        time.time() - start_time
    )

    print(
        f"SUCCESSFULLY STORED: {os.path.basename(file_path)}"
    )
    return document_id


# -------------------------------
# GENERAL CHAT TOOL
# -------------------------------

def general_chat(question):

    response = (
        groq_client.chat.completions.create(

            messages=[
                {
                    "role": "system",
                    "content":
                    (
                        "You are a professional "
                        "and helpful AI assistant."
                    )
                },
                {
                    "role": "user",
                    "content": question
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


# -------------------------------
# SUMMARY TOOL
# -------------------------------

def summary_tool():

    return (
        "Provide a detailed summary "
        "of the uploaded legal documents."
    )


# -------------------------------
# LEGAL RESEARCH TOOL
# -------------------------------

def legal_research_tool(question):

    return (
        "Provide professional legal analysis, "
        "key legal reasoning, implications, "
        "and important observations.\n\n"
        f"User Query:\n{question}"
    )


# -------------------------------
# ASK QUESTION
# -------------------------------

def ask_question(question,history,session_id):

    conversation_history = summarize_memory(history[-15:])
    
    # -------------------------------
    # SMART QUERY CLASSIFIER
    # -------------------------------

    document_keywords = [

        "document",
        "documents",
        "pdf",
        "file",
        "files",
        "case",
        "court",
        "judgement",
        "agreement",
        "contract",
        "research paper",
        "uploaded",
        "both documents",
        "these documents",
        "summarize",
        "summary",
        "explain",
        "details"
    ]

    question_lower = question.lower()

    is_document_query = any(

        keyword in question_lower

        for keyword in document_keywords
    )

    if is_document_query:

        query_type = "LEGAL_RAG"

    else:

        classifier_prompt = f"""
        Classify the query into ONLY one category:

        GENERAL_CHAT
        LEGAL_RAG
        DOCUMENT_SUMMARY
        LEGAL_RESEARCH

        Conversation Context:
        {conversation_history}

        Current Query:
        {question}
        """

        classifier_response = (
            groq_client.chat.completions.create(

                messages=[
                    {
                        "role": "user",
                        "content": classifier_prompt
                    }
                ],

                model="llama-3.1-8b-instant"
            )
        )

        query_type = (
            classifier_response
            .choices[0]
            .message
            .content
            .strip()
            .upper()
        )

    print("QUERY TYPE:", query_type)

    # -------------------------------
    # ROUTING
    # -------------------------------

    if "GENERAL_CHAT" in query_type:

        return general_chat(question)
    
    workflow_plan = create_workflow_plan(question)
    
    print("WORKFLOW PLAN:")

    print(workflow_plan)
    
    if "DOCUMENT_SUMMARY" in query_type:

        question = summary_tool()

    if "LEGAL_RESEARCH" in query_type:

        question = legal_research_tool(
            question
        )

    # -------------------------------
    # PINECONE SEARCH
    # -------------------------------

    planned_queries = plan_query(question)

    all_matches = []

    for q in planned_queries:

        query_embedding = create_embedding(q,input_type="query")

        results = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True,
        namespace=session_id
    )

        all_matches.extend(
            results["matches"]
        )
    
    unique_matches = {}

    for match in all_matches:

        unique_matches[
            match["id"]
        ] = match

    matches = list(
        unique_matches.values()
    )

    # -------------------------------
    # SORT BY RELEVANCE SCORE
    # -------------------------------

    matches.sort(

        key=lambda x: x["score"],

        reverse=True
    )

    # -------------------------------
    # LIMIT CONTEXT SIZE
    # -------------------------------

    matches = matches[:10]

    print(
        "MATCHES:",
        len(matches)
    )

    if len(matches) == 0:

        prompt = f"""
        You are LexAI, a legal AI assistant.

        The user asked:
        {question}

        No uploaded documents contain relevant information.

        Answer the question normally and helpfully.
        """

        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful legal AI assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
        )

        return completion.choices[0].message.content

    # -------------------------------
    # CONTEXT
    # -------------------------------

    context = ""

    citations = []

    seen_documents = set()

    seen_chunks = set()

    for match in matches:

        metadata = match["metadata"]

        source = metadata.get(
            "source",
            "Unknown"
        )

        text = metadata.get(
            "text",
            ""
        )

        # Avoid duplicate chunks
        if text in seen_chunks:

            continue

        seen_chunks.add(text)

        # Add document header once
        if source not in seen_documents:

            context += (
                f"\n===== DOCUMENT: {source} =====\n"
            )

            seen_documents.add(source)

        context += text + "\n\n"

        if source not in citations:

            citations.append(source)
    
    # -------------------------------
    # REFLECTION CHECK
    # -------------------------------

    has_enough_context = reflection_check(
        question,
        context
    )

    print(
        "REFLECTION RESULT:",
        has_enough_context
    )

    # -------------------------------
    # RETRIEVAL RETRY
    # -------------------------------

    if not has_enough_context:

        print(
            "RETRYING RETRIEVAL..."
        )

        retry_query = (
            question
            + " detailed legal analysis"
        )

        retry_embedding = create_embedding(
            retry_query,
            input_type="query"
        )

        retry_results = index.query(

            vector=retry_embedding,

            top_k=5,

            include_metadata=True,

            namespace=session_id
        )

        for match in retry_results["matches"]:

            metadata = match["metadata"]

            text = metadata.get(
                "text",
                ""
            )

            if text not in seen_chunks:

                context += text + "\n\n"

                seen_chunks.add(text)
        
    context = context[:12000]

    tool_outputs = []

    selected_tools = ["none"]

    tool_keywords = [
        "termination",
        "payment",
        "liability"
    ]

    if any(
        keyword in question.lower()
        for keyword in tool_keywords
    ):

        selected_tools = route_tools(
            question
        )

    print(
        "SELECTED TOOLS:",
        selected_tools
    )

    for tool in selected_tools:

        if tool == "termination_clause_tool":

            output = extract_clause_tool(
                context,
                "termination"
            )

            tool_outputs.append(
                output
            )

        elif tool == "payment_clause_tool":

            output = extract_clause_tool(
                context,
                "payment"
            )

            tool_outputs.append(
                output
            )

        elif tool == "liability_clause_tool":

            output = extract_clause_tool(
                context,
                "liability"
            )

            tool_outputs.append(
                output
            )

    tool_output = "\n\n".join(
        tool_outputs
    )

    tool_output = tool_output[:3000]

    # -------------------------------
    # FINAL PROMPT
    # -------------------------------

    prompt = f"""
    You are LexAI, a professional legal AI assistant.

    You have access to:
    1. Previous conversation history
    2. Uploaded legal documents

    Use BOTH to answer naturally, intelligently, and conversationally.

    STRICT RULES:
    1. Answer primarily from retrieved context.
    2. Multiple uploaded PDFs may exist.
    3. Use document separation internally only.
    4. Do NOT mention DOCUMENT headers.
    5. Do NOT mention internal retrieval structure.
    6. Maintain conversational continuity.
    7. Remember previous discussion context.
    8. If the user refers to earlier discussion,
    use conversation history to understand it.
    9. Keep responses clean, natural, and professional.
    10. Do NOT hallucinate.
    11. If information is unavailable say:
        "The uploaded documents do not contain this information."
    12. If Specialized Tool Output exists, prioritize it carefully during reasoning.

    Conversation History:
    {conversation_history}

    Workflow Plan:
    {workflow_plan}

    Retrieved Context:
    {context}

    Specialized Tool Output:
    {tool_output}

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

    final_answer = (
        response
        .choices[0]
        .message
        .content
    )

    if citations:

        final_answer += (
            "\n\n<sub>Sources: "
            + ", ".join(citations)
            + "</sub>"
        )

    return final_answer