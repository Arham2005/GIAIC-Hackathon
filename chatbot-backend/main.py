"""
RAG Chatbot Backend - FREE VERSION with Sentence Transformers
Fixed Qdrant compatibility
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import psycopg2
from psycopg2.extras import RealDictCursor
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# FREE embedding model (runs locally, no API cost!)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
EMBEDDING_DIM = 384  # Dimension for all-MiniLM-L6-v2

COLLECTION_NAME = "book_chapters"
CHAT_MODEL = "gpt-4o-mini"

# Database connection
def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database and Qdrant
    init_database()
    init_qdrant_collection()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(title="RAG Chatbot API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    selected_text: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[dict]

class IndexRequest(BaseModel):
    chapter_id: str
    title: str
    content: str

# Initialize database
def init_database():
    """Create chat history table"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            selected_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized")

# Initialize Qdrant collection
def init_qdrant_collection():
    """Create Qdrant collection for embeddings"""
    try:
        collections = qdrant_client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )
            print(f"✅ Created Qdrant collection: {COLLECTION_NAME}")
        else:
            print(f"✅ Qdrant collection exists: {COLLECTION_NAME}")
    except Exception as e:
        print(f"⚠️ Qdrant initialization: {e}")

# FREE Embedding function (no API cost!)
def get_embedding(text: str) -> List[float]:
    """Generate embedding using FREE local model"""
    embedding = embedding_model.encode(text)
    return embedding.tolist()

# API Routes
@app.get("/")
async def root():
    return {
        "message": "RAG Chatbot API - FREE Edition with Local Embeddings",
        "status": "running",
        "embedding_model": "all-MiniLM-L6-v2 (FREE)"
    }

@app.post("/index")
async def index_chapter(request: IndexRequest):
    """Index a chapter into Qdrant"""
    try:
        # Generate embedding (FREE - runs locally!)
        embedding = get_embedding(request.content)
        
        # Create point for Qdrant
        point_id = str(uuid.uuid4())
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "chapter_id": request.chapter_id,
                "title": request.title,
                "content": request.content[:1000],
                "full_content": request.content
            }
        )
        
        # Upload to Qdrant
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[point]
        )
        
        return {
            "status": "success",
            "chapter_id": request.chapter_id,
            "point_id": point_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """Handle chat request with RAG"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Determine query text
        query_text = request.selected_text if request.selected_text else request.message
        
        # Generate embedding for query (FREE!)
        query_embedding = get_embedding(query_text)
        
        # Search Qdrant - try both old and new API
        # Search Qdrant using query_points (v1.16+)
        from qdrant_client.models import QueryRequest, VectorInput
        
        search_response = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=3
        )
        
        search_results = search_response.points

        
        # Extract relevant context
        context_parts = []
        sources = []
        
        for result in search_results:
            context_parts.append(result.payload["full_content"])
            sources.append({
                "chapter_id": result.payload["chapter_id"],
                "title": result.payload["title"],
                "score": result.score
            })
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Build prompt
        system_prompt = """You are an AI assistant helping students learn about Physical AI and Humanoid Robotics. 
Answer questions based on the provided book content. Be clear, educational, and concise.
If the user selected specific text, focus your answer on that text."""
        
        user_prompt = f"""Context from the book:
{context}

User's question: {request.message}
"""
        
        if request.selected_text:
            user_prompt += f"\n\nUser selected this text: {request.selected_text}"
        
        # Get response from OpenAI
        completion = openai_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        bot_response = completion.choices[0].message.content
        
        # Save to database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO chat_history (session_id, user_message, bot_response, selected_text)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, request.message, bot_response, request.selected_text)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        return ChatResponse(
            response=bot_response,
            session_id=session_id,
            sources=sources
        )
    
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get chat history for a session"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            """
            SELECT user_message, bot_response, selected_text, created_at
            FROM chat_history
            WHERE session_id = %s
            ORDER BY created_at ASC
            """,
            (session_id,)
        )
        
        history = cur.fetchall()
        cur.close()
        conn.close()
        
        return {"session_id": session_id, "history": history}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "qdrant": "connected",
        "database": "connected",
        "embedding": "local (FREE)",
        "chat": "openai (gpt-4o-mini)"
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
    
    try:
        response = gemini_model.generate_content(prompt)
        return {
            "original_text": text,
            "translated_text": response.text.strip(),
            "target_language": target_language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)