
"""
Vector Service Implementation for AMAS
"""

import asyncio
import json
import logging
import os
import pickle
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import faiss
    import sentence_transformers

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available, using fallback vector operations")

logger = logging.getLogger(__name__)


class VectorService:
    """
    Vector Service for AMAS Intelligence System.
    Manages FAISS index and sentence transformer model for vector operations.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.index_path = config.get("index_path", "/app/faiss_index")
        self.embedding_model_name = config.get(
            "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.index = None
        self.embedding_model = None
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        self.documents = []
        self.metadata = []
        self.is_initialized = False

    async def initialize(self):
        """
        Initialize the vector service by loading or creating the FAISS index
        and the embedding model.
        """
        if self.is_initialized:
            logger.info("Vector service already initialized.")
            return

        try:
            if FAISS_AVAILABLE:
                await self._load_or_create_index()
                await self._load_embedding_model()
                self.is_initialized = True
                logger.info("Vector service initialized successfully.")
            else:
                logger.warning("FAISS not available, vector service operating in fallback (simulated) mode.")
                self.is_initialized = True # Mark as initialized even in fallback

        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise

    async def _load_or_create_index(self):
        """
        Load existing FAISS index or create a new one if it doesn't exist.
        """
        try:
            os.makedirs(self.index_path, exist_ok=True)
            index_file = os.path.join(self.index_path, "faiss_index.bin")
            metadata_file = os.path.join(self.index_path, "metadata.json")

            if os.path.exists(index_file):
                self.index = faiss.read_index(index_file)
                self.dimension = self.index.d

                if os.path.exists(metadata_file):
                    with open(metadata_file, "r") as f:
                        self.metadata = json.load(f)

                logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors.")
            else:
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
                logger.info("Created new FAISS index.")

        except Exception as e:
            logger.error(f"Error loading/creating index: {e}")
            raise

    async def _load_embedding_model(self):
        """
        Load the sentence transformer embedding model.
        """
        try:
            if FAISS_AVAILABLE:
                self.embedding_model = sentence_transformers.SentenceTransformer(
                    self.embedding_model_name
                )
                logger.info(f"Loaded embedding model: {self.embedding_model_name}")
            else:
                logger.warning("Sentence transformers not available.")

        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the vector service.
        """
        status = "healthy" if self.is_initialized else "uninitialized"
        if FAISS_AVAILABLE and self.index is None:
            status = "degraded" # Index not loaded/created yet

        return {
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "vector",
            "index_size": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "model": self.embedding_model_name,
            "faiss_available": FAISS_AVAILABLE,
        }

    async def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add documents to the vector index.
        """
        if not self.is_initialized or not FAISS_AVAILABLE or not self.embedding_model:
            return {"success": False, "error": "Vector service not fully operational.", "timestamp": datetime.utcnow().isoformat()}

        try:
            texts = [doc.get("content", "") for doc in documents]
            embeddings = self.embedding_model.encode(texts)

            faiss.normalize_L2(embeddings)

            self.index.add(embeddings.astype("float32"))

            for i, doc in enumerate(documents):
                self.metadata.append(
                    {
                        "id": doc.get("id", f"doc_{len(self.metadata)}"),
                        "content": doc.get("content", ""),
                        "metadata": doc.get("metadata", {}),
                        "index": self.index.ntotal - len(documents) + i,
                    }
                )

            await self._save_index()

            return {
                "success": True,
                "documents_added": len(documents),
                "total_documents": self.index.ntotal,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return {"success": False, "error": str(e), "timestamp": datetime.utcnow().isoformat()}

    async def semantic_search(self, query: str, limit: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform semantic search using vector embeddings.
        """
        if not self.is_initialized or not FAISS_AVAILABLE or not self.embedding_model:
            logger.warning("Vector service not fully operational for semantic search. Returning simulated results.")
            return [
                {"content": f"Simulated semantic result 1 for {query}", "score": 0.9, "metadata": {"source": "simulated"}, "entities": []},
                {"content": f"Simulated semantic result 2 for {query}", "score": 0.8, "metadata": {"source": "simulated"}, "entities": []},
            ]

        try:
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)

            scores, indices = self.index.search(query_embedding.astype("float32"), limit)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.metadata) and score >= threshold:
                    doc_meta = self.metadata[idx]
                    results.append(
                        {
                            "id": doc_meta["id"],
                            "content": doc_meta["content"],
                            "metadata": doc_meta["metadata"],
                            "score": float(score),
                            "index": int(idx),
                        }
                    )
            return results

        except Exception as e:
            logger.error(f"Error during semantic search: {e}")
            return []

    async def keyword_search(self, query: str, limit: int = 10, threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Perform keyword search (simulated for now, could integrate with a text search engine).
        """
        logger.info(f"VectorService: Performing keyword search for \'{query}\' (limit={limit}, threshold={threshold})")
        # This is a placeholder. In a real system, this would integrate with a dedicated text search engine (e.g., Elasticsearch, Lucene)
        return [
            {"content": f"Simulated keyword result 1 for {query}", "score": 0.75, "metadata": {"source": "simulated"}, "entities": []},
        ]

    async def hybrid_search(self, semantic_query: str, keyword_query: str, limit: int = 10, threshold: float = 0.65) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword approaches.
        """
        logger.info(f"VectorService: Performing hybrid search for semantic=\'{semantic_query}\' keyword=\'{keyword_query}\'")
        semantic_results = await self.semantic_search(semantic_query, limit // 2, threshold)
        keyword_results = await self.keyword_search(keyword_query, limit // 2, threshold)
        # Simple merge, more advanced fusion logic could be applied
        return list({v['content']:v for v in semantic_results + keyword_results}.values())

    async def search(self, query: str, limit: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Generic search method, defaults to semantic search.
        """
        return await self.semantic_search(query, limit, threshold)

    async def _save_index(self):
        """
        Save FAISS index and metadata to disk.
        """
        try:
            if self.index:
                index_file = os.path.join(self.index_path, "faiss_index.bin")
                faiss.write_index(self.index, index_file)

                metadata_file = os.path.join(self.index_path, "metadata.json")
                with open(metadata_file, "w") as f:
                    json.dump(self.metadata, f, indent=2)

                logger.info("Index and metadata saved successfully.")

        except Exception as e:
            logger.error(f"Error saving index: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get vector service statistics.
        """
        return {
            "total_documents": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "model": self.embedding_model_name,
            "index_path": self.index_path,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def close(self):
        """
        Clean up resources and shut down the vector service.
        """
        logger.info("Closing VectorService.")
        self.index = None
        self.embedding_model = None
        self.documents = []
        self.metadata = []
        self.is_initialized = False
        logger.info("VectorService closed.")


