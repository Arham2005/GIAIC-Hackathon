"""
RAG Chatbot Backend for Physical AI Book
FastAPI + Qdrant + Gemini (FREE)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import google.generativeai as genai
from datetime import datetime
import hashlib
import glob
import numpy as np

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Physical AI RAG API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Qdrant
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

COLLECTION_NAME = "physical_ai_book"
chat_history = []

# Models
class ChatRequest(BaseModel):
    message: str
    selected_text: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[dict]

class IndexRequest(BaseModel):
    force_reindex: bool = False

# Helper functions
def create_embeddings_gemini(text: str) -> List[float]:
    """Create embeddings using Gemini"""
    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    try:
        qdrant_client.get_collection(COLLECTION_NAME)
        print(f"✅ Collection '{COLLECTION_NAME}' exists")
    except:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=768,  # Gemini embedding dimension
                distance=Distance.COSINE
            )
        )
        print(f"✅ Created collection '{COLLECTION_NAME}'")

@app.get("/")
def read_root():
    return {
        "message": "Physical AI RAG API (Gemini-powered)",
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Health check"""
    try:
        qdrant_client.get_collection(COLLECTION_NAME)
        qdrant_status = "connected"
    except:
        qdrant_status = "disconnected"
    
    return {
        "status": "healthy",
        "qdrant": qdrant_status,
        "ai_provider": "Gemini"
    }

@app.post("/index")
async def index_documents(request: IndexRequest):
    """Index documents using Gemini embeddings"""
    
    docs_path = r"C:\Users\DELL\Desktop\Documents\book-project\docs"
    
    if not os.path.exists(docs_path):
        raise HTTPException(status_code=404, detail="Docs folder not found")
    
    indexed_chunks = 0
    indexed_files = []
    
    md_files = glob.glob(os.path.join(docs_path, "*.md"))
    
    for file_path in md_files:
        md_file = os.path.basename(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip() or len(content) < 100:
                continue
            
            chunks = chunk_text(content)
            
            if not chunks:
                continue
            
            for i, chunk in enumerate(chunks):
                try:
                    # Create embedding with Gemini
                    embedding = create_embeddings_gemini(chunk)
                    
                    chunk_id = hashlib.md5(f"{md_file}_{i}".encode()).hexdigest()
                    
                    qdrant_client.upsert(
                        collection_name=COLLECTION_NAME,
                        points=[
                            PointStruct(
                                id=chunk_id,
                                vector=embedding,
                                payload={
                                    "text": chunk,
                                    "source": md_file,
                                    "chunk_index": i
                                }
                            )
                        ]
                    )
                    
                    indexed_chunks += 1
                    
                except Exception as e:
                    print(f"⚠️ Error embedding chunk {i} of {md_file}: {str(e)}")
                    continue
            
            indexed_files.append(md_file)
            print(f"✅ Indexed {md_file}: {len(chunks)} chunks")
            
        except Exception as e:
            print(f"❌ Error indexing {md_file}: {str(e)}")
            continue
    
    return {
        "status": "success",
        "indexed_files": len(indexed_files),
        "file_names": indexed_files,
        "total_chunks": indexed_chunks
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat with Gemini"""
    
    query = request.message
    
    if request.selected_text:
        context = request.selected_text
        sources = [{"source": "selected_text", "text": request.selected_text[:200]}]
    else:
        # Create query embedding
        query_embedding = create_embeddings_gemini(query)
        
        # Search Qdrant
        search_results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=3
        )
        
        context_chunks = []
        sources = []
        
        for result in search_results:
            context_chunks.append(result.payload["text"])
            sources.append({
                "source": result.payload["source"],
                "text": result.payload["text"][:200] + "...",
                "score": float(result.score)
            })
        
        context = "\n\n".join(context_chunks)
    
    # Generate response with Gemini
    prompt = f"""You are an expert AI assistant for a textbook on Physical AI and Humanoid Robotics.
Answer the question based on the provided context from the book. Be accurate and educational.

Context:
{context}

Question: {query}

Answer:"""
    
    response = gemini_model.generate_content(prompt)
    response_text = response.text
    
    chat_history.append({
        "timestamp": datetime.now().isoformat(),
        "message": query,
        "response": response_text
    })
    
    return ChatResponse(
        response=response_text,
        sources=sources
    )

@app.get("/stats")
def get_stats():
    """Get stats"""
    try:
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        points_count = collection_info.points_count
    except:
        points_count = 0
    
    return {
        "total_chats": len(chat_history),
        "indexed_chunks": points_count,
        "ai_provider": "Gemini"
    }

@app.post("/translate")
async def translate_text(request: dict):
    """Translate text to Urdu using Gemini"""
    text = request.get("text", "")
    target_language = request.get("target_language", "urdu")
    
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    prompt = f"""Translate the following English text to {target_language}. 
    Maintain technical terminology where appropriate.
    Only return the translated text, nothing else.
    
    Text: {text}
    
    Translation:"""
    
    response = gemini_model.generate_content(prompt)
    
    return {
        "original_text": text,
        "translated_text": response.text.strip(),
        "target_language": target_language
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)