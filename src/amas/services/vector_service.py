"""
Vector Service Implementation for AMAS
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

try:
    import faiss
    import sentence_transformers

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available, using fallback vector operations")

logger = logging.getLogger(__name__)


class VectorService:
    """Vector Service for AMAS Intelligence System"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Use index_path from config, or default to local path (not URL)
        # If vector_service_url is provided and is a URL, use default local path
        vector_url = config.get("vector_service_url", "")
        if vector_url and (vector_url.startswith("http://") or vector_url.startswith("https://")):
            # URL provided, use local default path
            import pathlib
            self.index_path = str(pathlib.Path("data/faiss_index").absolute())
        else:
            # Use provided path or default
            self.index_path = config.get("index_path", config.get("vector_service_url", "data/faiss_index"))
        self.embedding_model_name = config.get(
            "embedding_model", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.index = None
        self.embedding_model = None
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        self.documents = []
        self.metadata = []

    async def initialize(self):
        """Initialize the vector service"""
        try:
            if FAISS_AVAILABLE:
                # Load or create FAISS index
                await self._load_or_create_index()

                # Load embedding model
                await self._load_embedding_model()

                logger.info("Vector service initialized successfully")
            else:
                logger.warning("FAISS not available, using fallback mode")

        except Exception as e:
            logger.error(f"Failed to initialize vector service: {e}")
            raise

    async def _load_or_create_index(self):
        """Load existing index or create new one"""
        try:
            index_file = os.path.join(self.index_path, "faiss_index.bin")
            metadata_file = os.path.join(self.index_path, "metadata.json")

            if os.path.exists(index_file):
                # Load existing index
                self.index = faiss.read_index(index_file)
                self.dimension = self.index.d

                # Load metadata
                if os.path.exists(metadata_file):
                    with open(metadata_file, "r") as f:
                        self.metadata = json.load(f)

                logger.info(
                    f"Loaded existing FAISS index with {self.index.ntotal} vectors"
                )
            else:
                # Create new index
                os.makedirs(self.index_path, exist_ok=True)
                self.index = faiss.IndexFlatIP(
                    self.dimension
                )  # Inner product for cosine similarity
                logger.info("Created new FAISS index")

        except Exception as e:
            logger.error(f"Error loading/creating index: {e}")
            raise

    async def _load_embedding_model(self):
        """Load sentence transformer model"""
        try:
            if FAISS_AVAILABLE:
                self.embedding_model = sentence_transformers.SentenceTransformer(
                    self.embedding_model_name
                )
                logger.info(f"Loaded embedding model: {self.embedding_model_name}")
            else:
                logger.warning("Sentence transformers not available")

        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check vector service health"""
        try:
            status = {
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "vector",
                "index_size": self.index.ntotal if self.index else 0,
                "dimension": self.dimension,
                "model": self.embedding_model_name,
            }
            return status
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "vector",
            }

    async def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add documents to the vector index"""
        try:
            if not FAISS_AVAILABLE or not self.embedding_model:
                return {
                    "success": False,
                    "error": "Vector service not properly initialized",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            texts = [doc.get("content", "") for doc in documents]
            embeddings = self.embedding_model.encode(texts)

            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)

            # Add to index
            self.index.add(embeddings.astype("float32"))

            # Store metadata
            for i, doc in enumerate(documents):
                self.metadata.append(
                    {
                        "id": doc.get("id", f"doc_{len(self.metadata)}"),
                        "content": doc.get("content", ""),
                        "metadata": doc.get("metadata", {}),
                        "index": self.index.ntotal - len(documents) + i,
                    }
                )

            # Save index and metadata
            await self._save_index()

            return {
                "success": True,
                "documents_added": len(documents),
                "total_documents": self.index.ntotal,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def search(
        self, query: str, top_k: int = 5, threshold: float = 0.7
    ) -> Dict[str, Any]:
        """Search for similar documents"""
        try:
            if not FAISS_AVAILABLE or not self.embedding_model:
                return {
                    "success": False,
                    "error": "Vector service not properly initialized",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)

            # Search
            scores, indices = self.index.search(
                query_embedding.astype("float32"), top_k
            )

            # Format results
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

            return {
                "success": True,
                "query": query,
                "results": results,
                "total_found": len(results),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _save_index(self):
        """Save index and metadata to disk"""
        try:
            if self.index:
                # Save FAISS index
                index_file = os.path.join(self.index_path, "faiss_index.bin")
                faiss.write_index(self.index, index_file)

                # Save metadata
                metadata_file = os.path.join(self.index_path, "metadata.json")
                with open(metadata_file, "w") as f:
                    json.dump(self.metadata, f, indent=2)

                logger.info("Index and metadata saved successfully")

        except Exception as e:
            logger.error(f"Error saving index: {e}")

    async def get_stats(self) -> Dict[str, Any]:
        """Get vector service statistics"""
        return {
            "total_documents": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "model": self.embedding_model_name,
            "index_path": self.index_path,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def close(self):
        """Close vector service and cleanup resources"""
        try:
            # Save index before closing if it exists
            if self.index:
                await self._save_index()
            logger.info("Vector service closed successfully")
        except Exception as e:
            logger.error(f"Error closing vector service: {e}")
