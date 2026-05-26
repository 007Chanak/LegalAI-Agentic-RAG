from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from pydantic import BaseModel

from app.rag import (
    process_pdf,
    ask_question
)

import os
import uuid


# -------------------------------
# FASTAPI APP
# -------------------------------

app = FastAPI()


# -------------------------------
# CORS
# -------------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# -------------------------------
# UPLOAD DIRECTORY
# -------------------------------

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# -------------------------------
# HOME ROUTE
# -------------------------------

@app.get("/")
def home():

    return {

        "message":
        "Legal RAG API Running"
    }


# -------------------------------
# PDF UPLOAD ROUTE
# -------------------------------

@app.post("/upload")
async def upload_pdf(

    file: UploadFile = File(...),

    session_id: str = Form(...)
):

    try:

        print("UPLOAD STARTED")

        # -------------------------------
        # VALIDATE PDF
        # -------------------------------

        if not file.filename.lower().endswith(".pdf"):

            raise HTTPException(

                status_code=400,

                detail="Only PDF files allowed."
            )

        unique_id = str(uuid.uuid4())

        filename = (
            f"{unique_id}_{file.filename}"
        )

        file_path = os.path.join(
            UPLOAD_DIR,
            filename
        )

        # -------------------------------
        # SAVE FILE
        # -------------------------------

        with open(file_path, "wb") as f:

            content = await file.read()

            f.write(content)

        print(
            f"FILE SAVED: {file_path}"
        )

        # -------------------------------
        # PROCESS PDF
        # -------------------------------

        document_id = process_pdf(
            file_path,
            session_id
        )

        if not document_id:

            raise HTTPException(

                status_code=400,

                detail=(
                    "Could not extract text "
                    "from PDF."
                )
            )

        print(
            "PDF PROCESSED SUCCESSFULLY"
        )

        return {

            "message":
            "PDF processed successfully",

            "filename":
            file.filename,

            "document_id":
            document_id
        }

    except HTTPException:

        raise

    except Exception as e:

        print("UPLOAD ERROR:", str(e))

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# -------------------------------
# CHAT REQUEST MODEL
# -------------------------------

class ChatRequest(BaseModel):

    question: str

    history: list

    session_id: str


# -------------------------------
# ASK ROUTE
# -------------------------------

@app.post("/ask")
def ask(chat: ChatRequest):

    try:

        print(
            "QUESTION RECEIVED:",
            chat.question
        )

        answer = ask_question(

            chat.question,

            chat.history,

            chat.session_id
        )

        return {

            "question":
            chat.question,

            "answer":
            answer
        }

    except Exception as e:

        print("ASK ERROR:", str(e))

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# -------------------------------
# LOCAL RUN
# -------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "app.main:app",

        host="0.0.0.0",

        port=8000,

        reload=True
    )