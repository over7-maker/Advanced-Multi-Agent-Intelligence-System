"""
Vector Service for AMAS
Provides vector search capabilities using FAISS
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import faiss
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AMAS Vector Service", version="1.0.0")

# Global variables
vectorizer = None
index = None
documents = []
vector_data_path = os.getenv("VECTOR_DATA_PATH", "/data/vectors")

class VectorSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    threshold: float = 0.0

class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    query: str

class DocumentIndexRequest(BaseModel):
    documents: List[str]
    metadata: Optional[List[Dict[str, Any]]] = None

class DocumentIndexResponse(BaseModel):
    indexed_count: int
    total_documents: int
    index_size: int

def initialize_vectorizer():
    """Initialize the TF-IDF vectorizer"""
    global vectorizer
    vectorizer = TfidfVectorizer(
        max_features=10000, stop_words="english", ngram_range=(1, 2)
    )
    logger.info("Vectorizer initialized")

def initialize_index():
    """Initialize the FAISS index"""
    global index
    # Use a simple flat index for now
    # In production, you might want to use IVF or HNSW
    index = faiss.IndexFlatIP(10000)  # Inner product similarity
    logger.info("FAISS index initialized")

def load_existing_data():
    """Load existing vector data if available"""
    global documents, vectorizer, index

    try:
        # Load documents
        docs_file = os.path.join(vector_data_path, "documents.json")
        if os.path.exists(docs_file):
            with open(docs_file, "r") as f:
                documents = json.load(f)
            logger.info(f"Loaded {len(documents)} existing documents")

        # Load vectors
        vectors_file = os.path.join(vector_data_path, "vectors.npy")
        if os.path.exists(vectors_file):
            vectors = np.load(vectors_file)
            if len(vectors) > 0:
                index.add(vectors.astype("float32"))
                logger.info(f"Loaded {len(vectors)} existing vectors")

        # Load vectorizer
        vectorizer_file = os.path.join(vector_data_path, "vectorizer.pkl")
        if os.path.exists(vectorizer_file):
            import pickle

            with open(vectorizer_file, "rb") as f:
                vectorizer = pickle.load(f)
            logger.info("Loaded existing vectorizer")

    except Exception as e:
        logger.warning(f"Could not load existing data: {e}")

def save_data():
    """Save vector data to disk"""
    try:
        os.makedirs(vector_data_path, exist_ok=True)

        # Save documents
        with open(os.path.join(vector_data_path, "documents.json"), "w") as f:
            json.dump(documents, f)

        # Save vectors
        if index.ntotal > 0:
            vectors = index.reconstruct_n(0, index.ntotal)
            np.save(os.path.join(vector_data_path, "vectors.npy"), vectors)

        # Save vectorizer
        import pickle

        with open(os.path.join(vector_data_path, "vectorizer.pkl"), "wb") as f:
            pickle.dump(vectorizer, f)

        logger.info("Data saved successfully")

    except Exception as e:
        logger.error(f"Could not save data: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize the vector service on startup"""
    logger.info("Starting AMAS Vector Service...")
    initialize_vectorizer()
    initialize_index()
    load_existing_data()
    logger.info("Vector service started successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "vector",
        "documents_count": len(documents),
        "index_size": index.ntotal if index else 0,
    }

@app.post("/index", response_model=DocumentIndexResponse)
async def index_documents(request: DocumentIndexRequest):
    """Index documents for vector search"""
    try:
        global documents, vectorizer, index

        # Add new documents
        new_docs = request.documents
        documents.extend(new_docs)

        # Fit vectorizer on all documents
        all_vectors = vectorizer.fit_transform(documents)

        # Clear and rebuild index
        index.reset()
        vectors = all_vectors.toarray().astype("float32")
        index.add(vectors)

        # Save data
        save_data()

        return DocumentIndexResponse(
            indexed_count=len(new_docs),
            total_documents=len(documents),
            index_size=index.ntotal,
        )

    except Exception as e:
        logger.error(f"Error indexing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=VectorSearchResponse)
async def search_vectors(request: VectorSearchRequest):
    """Search for similar vectors"""
    try:
        if not vectorizer or index.ntotal == 0:
            return VectorSearchResponse(results=[], total=0, query=request.query)

        # Vectorize query
        query_vector = vectorizer.transform([request.query]).toarray().astype("float32")

        # Search
        scores, indices = index.search(query_vector, request.top_k)

        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and score >= request.threshold:
                results.append(
                    {
                        "document": documents[idx],
                        "score": float(score),
                        "index": int(idx),
                    }
                )

        return VectorSearchResponse(
            results=results, total=len(results), query=request.query
        )

    except Exception as e:
        logger.error(f"Error searching vectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Get vector service statistics"""
    return {
        "documents_count": len(documents),
        "index_size": index.ntotal if index else 0,
        "vectorizer_features": (
            vectorizer.get_feature_names_out().shape[0] if vectorizer else 0
        ),
    }

@app.delete("/clear")
async def clear_index():
    """Clear all indexed data"""
    global documents, index
    documents.clear()
    index.reset()
    save_data()
    return {"message": "Index cleared successfully"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
