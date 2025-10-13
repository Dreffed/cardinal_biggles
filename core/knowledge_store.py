"""
Knowledge Store for Cardinal Biggles
Manages document storage, retrieval, and semantic search
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json
import logging
from pathlib import Path
import asyncio
import pickle
import uuid

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Type of document stored"""
    RESEARCH_FINDING = "research_finding"
    AGENT_OUTPUT = "agent_output"
    WEB_CONTENT = "web_content"
    ACADEMIC_PAPER = "academic_paper"
    NEWS_ARTICLE = "news_article"
    BOOK_SUMMARY = "book_summary"
    REPORT = "report"
    OTHER = "other"


@dataclass
class Document:
    """Document stored in knowledge base"""
    id: str
    content: str
    document_type: DocumentType
    source: str  # agent_id or external source
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    parent_id: Optional[str] = None  # For hierarchical documents

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['document_type'] = self.document_type.value
        data['created_at'] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create from dictionary"""
        data = data.copy()
        data['document_type'] = DocumentType(data['document_type'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class SimpleKnowledgeStore:
    """
    Simple in-memory knowledge store with optional persistence
    Supports basic storage, retrieval, and text-based search
    """

    def __init__(
        self,
        persist_path: Optional[str] = None,
        auto_save: bool = True,
        enable_embeddings: bool = False
    ):
        """
        Initialize knowledge store

        Args:
            persist_path: Path to save/load knowledge store
            auto_save: Automatically save after each operation
            enable_embeddings: Enable embedding-based search (requires sentence-transformers)
        """
        self.persist_path = persist_path
        self.auto_save = auto_save
        self.enable_embeddings = enable_embeddings

        # Storage
        self.documents: Dict[str, Document] = {}  # id -> Document
        self.documents_by_source: Dict[str, List[str]] = {}  # source -> [doc_ids]
        self.documents_by_type: Dict[DocumentType, List[str]] = {
            t: [] for t in DocumentType
        }
        self.documents_by_tag: Dict[str, List[str]] = {}  # tag -> [doc_ids]

        # Embedding model
        self.embedding_model = None
        if enable_embeddings:
            self._initialize_embeddings()

        # Load existing data if available
        if persist_path and Path(persist_path).exists():
            self.load()

        logger.info(f"Knowledge store initialized (embeddings: {enable_embeddings})")

    def _initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            self.enable_embeddings = False

    async def add_document(
        self,
        content: str,
        source: str,
        document_type: DocumentType = DocumentType.OTHER,
        metadata: Dict[str, Any] = None,
        tags: List[str] = None,
        parent_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the knowledge store

        Args:
            content: Document content
            source: Source identifier (e.g., agent_id)
            document_type: Type of document
            metadata: Additional metadata
            tags: Tags for categorization
            parent_id: Parent document ID for hierarchical structure

        Returns:
            Document ID
        """
        # Generate ID
        doc_id = str(uuid.uuid4())

        # Generate embedding if enabled
        embedding = None
        if self.enable_embeddings and self.embedding_model:
            try:
                # Run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                embedding = await loop.run_in_executor(
                    None,
                    lambda: self.embedding_model.encode(content).tolist()
                )
            except Exception as e:
                logger.warning(f"Failed to generate embedding: {e}")

        # Create document
        document = Document(
            id=doc_id,
            content=content,
            document_type=document_type,
            source=source,
            metadata=metadata or {},
            tags=tags or [],
            embedding=embedding,
            parent_id=parent_id
        )

        # Store
        self.documents[doc_id] = document

        # Index by source
        if source not in self.documents_by_source:
            self.documents_by_source[source] = []
        self.documents_by_source[source].append(doc_id)

        # Index by type
        self.documents_by_type[document_type].append(doc_id)

        # Index by tags
        for tag in tags or []:
            if tag not in self.documents_by_tag:
                self.documents_by_tag[tag] = []
            self.documents_by_tag[tag].append(doc_id)

        logger.debug(f"Added document {doc_id} from {source}")

        # Auto-save if enabled
        if self.auto_save and self.persist_path:
            self.save()

        return doc_id

    async def add_documents_bulk(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Add multiple documents at once

        Args:
            documents: List of document data dicts

        Returns:
            List of document IDs
        """
        doc_ids = []
        for doc_data in documents:
            doc_id = await self.add_document(**doc_data)
            doc_ids.append(doc_id)
        return doc_ids

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID"""
        return self.documents.get(doc_id)

    def get_by_source(self, source: str) -> List[Document]:
        """Get all documents from a specific source"""
        doc_ids = self.documents_by_source.get(source, [])
        return [self.documents[doc_id] for doc_id in doc_ids]

    def get_by_type(self, document_type: DocumentType) -> List[Document]:
        """Get all documents of a specific type"""
        doc_ids = self.documents_by_type[document_type]
        return [self.documents[doc_id] for doc_id in doc_ids]

    def get_by_tag(self, tag: str) -> List[Document]:
        """Get all documents with a specific tag"""
        doc_ids = self.documents_by_tag.get(tag, [])
        return [self.documents[doc_id] for doc_id in doc_ids]

    def get_all(self) -> List[Document]:
        """Get all documents"""
        return list(self.documents.values())

    async def search(
        self,
        query: str,
        max_results: int = 10,
        document_type: Optional[DocumentType] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Search documents by query

        Args:
            query: Search query
            max_results: Maximum number of results
            document_type: Filter by document type
            source: Filter by source
            tags: Filter by tags

        Returns:
            List of matching documents, sorted by relevance
        """
        if self.enable_embeddings and self.embedding_model:
            return await self._semantic_search(
                query, max_results, document_type, source, tags
            )
        else:
            return await self._text_search(
                query, max_results, document_type, source, tags
            )

    async def _semantic_search(
        self,
        query: str,
        max_results: int,
        document_type: Optional[DocumentType],
        source: Optional[str],
        tags: Optional[List[str]]
    ) -> List[Document]:
        """Semantic search using embeddings"""
        try:
            # Generate query embedding
            loop = asyncio.get_event_loop()
            query_embedding = await loop.run_in_executor(
                None,
                lambda: self.embedding_model.encode(query).tolist()
            )

            # Filter documents
            candidates = self._apply_filters(document_type, source, tags)

            # Calculate similarities
            results = []
            for doc in candidates:
                if doc.embedding:
                    similarity = self._cosine_similarity(
                        query_embedding,
                        doc.embedding
                    )
                    results.append((doc, similarity))

            # Sort by similarity
            results.sort(key=lambda x: x[1], reverse=True)

            return [doc for doc, _ in results[:max_results]]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            # Fallback to text search
            return await self._text_search(
                query, max_results, document_type, source, tags
            )

    async def _text_search(
        self,
        query: str,
        max_results: int,
        document_type: Optional[DocumentType],
        source: Optional[str],
        tags: Optional[List[str]]
    ) -> List[Document]:
        """Simple text-based search"""
        # Filter documents
        candidates = self._apply_filters(document_type, source, tags)

        # Tokenize query
        query_terms = set(query.lower().split())

        # Score documents
        results = []
        for doc in candidates:
            content_terms = set(doc.content.lower().split())

            # Calculate overlap
            overlap = len(query_terms & content_terms)
            if overlap > 0:
                score = overlap / len(query_terms)
                results.append((doc, score))

        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in results[:max_results]]

    def _apply_filters(
        self,
        document_type: Optional[DocumentType],
        source: Optional[str],
        tags: Optional[List[str]]
    ) -> List[Document]:
        """Apply filters to document set"""
        candidates = list(self.documents.values())

        if document_type:
            candidates = [
                doc for doc in candidates
                if doc.document_type == document_type
            ]

        if source:
            candidates = [
                doc for doc in candidates
                if doc.source == source
            ]

        if tags:
            candidates = [
                doc for doc in candidates
                if any(tag in doc.tags for tag in tags)
            ]

        return candidates

    def _cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """Calculate cosine similarity between vectors"""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 * magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        if doc_id not in self.documents:
            return False

        doc = self.documents[doc_id]

        # Remove from storage
        del self.documents[doc_id]

        # Remove from indices
        if doc.source in self.documents_by_source:
            self.documents_by_source[doc.source].remove(doc_id)

        self.documents_by_type[doc.document_type].remove(doc_id)

        for tag in doc.tags:
            if tag in self.documents_by_tag:
                self.documents_by_tag[tag].remove(doc_id)

        logger.debug(f"Deleted document {doc_id}")

        # Auto-save if enabled
        if self.auto_save and self.persist_path:
            self.save()

        return True

    def update_document(
        self,
        doc_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Update a document"""
        if doc_id not in self.documents:
            return False

        doc = self.documents[doc_id]

        if content is not None:
            doc.content = content
            # Regenerate embedding if enabled
            if self.enable_embeddings and self.embedding_model:
                try:
                    doc.embedding = self.embedding_model.encode(content).tolist()
                except Exception as e:
                    logger.warning(f"Failed to regenerate embedding: {e}")

        if metadata is not None:
            doc.metadata.update(metadata)

        if tags is not None:
            # Remove old tag indices
            for tag in doc.tags:
                if tag in self.documents_by_tag:
                    self.documents_by_tag[tag].remove(doc_id)

            # Update tags
            doc.tags = tags

            # Add new tag indices
            for tag in tags:
                if tag not in self.documents_by_tag:
                    self.documents_by_tag[tag] = []
                self.documents_by_tag[tag].append(doc_id)

        logger.debug(f"Updated document {doc_id}")

        # Auto-save if enabled
        if self.auto_save and self.persist_path:
            self.save()

        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge store statistics"""
        return {
            'total_documents': len(self.documents),
            'by_type': {
                doc_type.value: len(doc_ids)
                for doc_type, doc_ids in self.documents_by_type.items()
                if doc_ids
            },
            'by_source': {
                source: len(doc_ids)
                for source, doc_ids in self.documents_by_source.items()
            },
            'total_sources': len(self.documents_by_source),
            'total_tags': len(self.documents_by_tag),
            'embeddings_enabled': self.enable_embeddings
        }

    def clear(self):
        """Clear all documents"""
        self.documents.clear()
        self.documents_by_source.clear()
        self.documents_by_type = {t: [] for t in DocumentType}
        self.documents_by_tag.clear()

        logger.info("Knowledge store cleared")

        if self.auto_save and self.persist_path:
            self.save()

    def save(self, filepath: Optional[str] = None):
        """
        Save knowledge store to disk

        Args:
            filepath: Optional custom filepath (uses persist_path if not provided)
        """
        save_path = filepath or self.persist_path
        if not save_path:
            logger.warning("No persist_path configured, cannot save")
            return

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare data for serialization
        data = {
            'documents': {
                doc_id: doc.to_dict()
                for doc_id, doc in self.documents.items()
            },
            'documents_by_source': self.documents_by_source,
            'documents_by_type': {
                doc_type.value: doc_ids
                for doc_type, doc_ids in self.documents_by_type.items()
            },
            'documents_by_tag': self.documents_by_tag,
            'metadata': {
                'saved_at': datetime.now().isoformat(),
                'embeddings_enabled': self.enable_embeddings
            }
        }

        # Save as JSON
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Knowledge store saved to {save_path}")

    def load(self, filepath: Optional[str] = None):
        """
        Load knowledge store from disk

        Args:
            filepath: Optional custom filepath (uses persist_path if not provided)
        """
        load_path = filepath or self.persist_path
        if not load_path:
            logger.warning("No persist_path configured, cannot load")
            return

        load_path = Path(load_path)
        if not load_path.exists():
            logger.warning(f"File not found: {load_path}")
            return

        try:
            with open(load_path, 'r') as f:
                data = json.load(f)

            # Restore documents
            self.documents = {
                doc_id: Document.from_dict(doc_data)
                for doc_id, doc_data in data['documents'].items()
            }

            # Restore indices
            self.documents_by_source = data['documents_by_source']
            self.documents_by_type = {
                DocumentType(doc_type): doc_ids
                for doc_type, doc_ids in data['documents_by_type'].items()
            }
            self.documents_by_tag = data['documents_by_tag']

            logger.info(
                f"Knowledge store loaded from {load_path} "
                f"({len(self.documents)} documents)"
            )

        except Exception as e:
            logger.error(f"Failed to load knowledge store: {e}")

    def export_markdown(
        self,
        document_type: Optional[DocumentType] = None,
        source: Optional[str] = None
    ) -> str:
        """
        Export documents as Markdown

        Args:
            document_type: Filter by document type
            source: Filter by source

        Returns:
            Markdown formatted string
        """
        # Filter documents
        documents = self._apply_filters(document_type, source, None)

        if not documents:
            return "No documents found."

        # Sort by creation date
        documents.sort(key=lambda d: d.created_at, reverse=True)

        lines = [f"# Knowledge Store Export\n"]
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        lines.append(f"*Total Documents: {len(documents)}*\n")

        # Group by type
        by_type = {}
        for doc in documents:
            if doc.document_type not in by_type:
                by_type[doc.document_type] = []
            by_type[doc.document_type].append(doc)

        for doc_type, docs in by_type.items():
            lines.append(f"\n## {doc_type.value.replace('_', ' ').title()}\n")

            for doc in docs:
                lines.append(f"\n### {doc.source} - {doc.created_at.strftime('%Y-%m-%d')}\n")

                if doc.tags:
                    tags_str = ", ".join(f"`{tag}`" for tag in doc.tags)
                    lines.append(f"*Tags: {tags_str}*\n")

                lines.append(f"\n{doc.content}\n")

                if doc.metadata.get('urls'):
                    lines.append("\n**References:**\n")
                    for url in doc.metadata['urls']:
                        lines.append(f"- {url}\n")

                lines.append("\n---\n")

        return "\n".join(lines)


# Convenience functions
def create_knowledge_store(
    persist_path: Optional[str] = "./data/knowledge_store.json",
    enable_embeddings: bool = False
) -> SimpleKnowledgeStore:
    """Create a knowledge store with default settings"""
    return SimpleKnowledgeStore(
        persist_path=persist_path,
        auto_save=True,
        enable_embeddings=enable_embeddings
    )


# Example usage
if __name__ == "__main__":
    async def main():
        # Create knowledge store
        store = create_knowledge_store(
            persist_path="./test_knowledge_store.json",
            enable_embeddings=False  # Set True if sentence-transformers installed
        )

        # Add documents
        doc_id1 = await store.add_document(
            content="Multi-agent systems are becoming increasingly popular in AI research.",
            source="research_agent",
            document_type=DocumentType.RESEARCH_FINDING,
            tags=["ai", "multi-agent", "research"]
        )

        doc_id2 = await store.add_document(
            content="LangChain provides a framework for building LLM applications.",
            source="research_agent",
            document_type=DocumentType.RESEARCH_FINDING,
            tags=["langchain", "llm", "framework"],
            metadata={"urls": ["https://langchain.com"]}
        )

        doc_id3 = await store.add_document(
            content="Vector databases like Pinecone and Qdrant are essential for RAG systems.",
            source="tech_scout",
            document_type=DocumentType.WEB_CONTENT,
            tags=["vector-db", "rag", "database"]
        )

        print(f"\nAdded {len(store.documents)} documents")

        # Search
        print("\n--- Search: 'multi-agent' ---")
        results = await store.search("multi-agent", max_results=5)
        for doc in results:
            print(f"- {doc.content[:80]}... (source: {doc.source})")

        # Get by source
        print("\n--- Documents from 'research_agent' ---")
        research_docs = store.get_by_source("research_agent")
        for doc in research_docs:
            print(f"- {doc.content[:80]}...")

        # Get by tag
        print("\n--- Documents tagged 'ai' ---")
        ai_docs = store.get_by_tag("ai")
        for doc in ai_docs:
            print(f"- {doc.content[:80]}...")

        # Statistics
        print("\n--- Statistics ---")
        stats = store.get_statistics()
        print(json.dumps(stats, indent=2))

        # Export as markdown
        print("\n--- Markdown Export ---")
        markdown = store.export_markdown()
        print(markdown[:500] + "...")

        # Save will happen automatically due to auto_save=True
        print(f"\nKnowledge store auto-saved to {store.persist_path}")

        # Test loading
        print("\n--- Testing Load ---")
        new_store = create_knowledge_store(persist_path="./test_knowledge_store.json")
        print(f"Loaded {len(new_store.documents)} documents")

    asyncio.run(main())
