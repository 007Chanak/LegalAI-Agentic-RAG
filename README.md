# LegalAI — Agentic Legal RAG System

⚠️ This project is built for research and learning purposes and does not provide professional legal advice.

LegalAI is an advanced Agentic Retrieval-Augmented Generation (RAG) system designed for intelligent legal document analysis, conversational legal research, and multi-document reasoning.

The project goes beyond traditional RAG pipelines by integrating:
- workflow planning
- adaptive retrieval
- reflection-based retry
- conversational memory
- multi-tool orchestration
- clause extraction pipelines

Built using FastAPI, Pinecone, Groq, Docker, AWS ECR, and AWS Fargate.

---

# Features

- Upload and analyze multiple legal PDFs
- Conversational legal document querying
- Multi-document reasoning
- Adaptive retrieval retry using reflection agents
- Workflow planning and tool orchestration
- Clause extraction pipelines
- Conversational memory summarization
- Cloud-native deployment architecture

---

# Tech Stack

## Backend
- Python
- FastAPI

## AI / LLM
- Groq API
- Llama 3.1 8B Instant

## Vector Database
- Pinecone

## PDF Processing
- pdfplumber
- PyPDF2

## Deployment
- Docker
- AWS ECR
- AWS ECS Fargate
- Amazon S3

---

# System Architecture

```text
User Query
    ↓
Memory Agent
    ↓
Workflow Planner
    ↓
Query Planner
    ↓
Vector Retrieval
    ↓
Reflection Agent
    ↓
Adaptive Retry
    ↓
Tool Router
    ↓
Multi-tool Execution
    ↓
Final Legal Reasoning
    ↓
Response
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/007Chanak/LegalAI-Agentic-RAG
```

```bash
cd LEGAL_AGENTIC_RAG
```

---

# Backend Setup

```bash
cd backend
```

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file inside `backend/`

```env
GROQ_API_KEY=your_groq_api_key

PINECONE_API_KEY=your_pinecone_api_key

PINECONE_INDEX=your_index_name
```

---

# Run Locally

```bash
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

---

# Docker Setup

## Build Docker Image

```bash
docker build -t legalai .
```

## Run Container

```bash
docker run -p 8000:8000 legalai
```

---

# Example Queries

- Summarize both documents
- Compare liability clauses in both agreements
- Explain all major legal concerns
- What was the payment issue in the second contract?
- Identify termination conditions across contracts
- Highlight legal risks in the agreement

---

# Future Improvements

- Hybrid Retrieval (Semantic + BM25)
- Reranking Pipelines
- Persistent Long-Term Memory
- Semantic Clause Extraction
- Citation-aware Reasoning
- Streaming Responses
- Async Workflow Execution

---

# Live Demo

Frontend:
[https://LegalAI-Agentic-RAG.com](http://legal-rag-frontend-v2.s3-website.ap-south-1.amazonaws.com/)

---

# Author

## Chanak Athmaraman

- GitHub: https://github.com/007Chanak
- LinkedIn: https://www.linkedin.com/in/chanak-athmaraman007/
