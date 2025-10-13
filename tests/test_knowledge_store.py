"""
Tests for Knowledge Store
"""

import pytest
from pathlib import Path


@pytest.mark.unit
class TestKnowledgeStore:
    """Test Knowledge Store functionality"""

    @pytest.mark.asyncio
    async def test_add_document(self, knowledge_store):
        """Test adding a document"""
        from core.knowledge_store import DocumentType

        doc_id = await knowledge_store.add_document(
            content="Test document content",
            source="test",
            document_type=DocumentType.RESEARCH_FINDING
        )

        assert doc_id is not None
        assert len(knowledge_store.documents) == 1

    @pytest.mark.asyncio
    async def test_get_document(self, populated_knowledge_store):
        """Test retrieving a document"""
        docs = populated_knowledge_store.get_all()

        assert len(docs) > 0

        doc_id = docs[0].id
        retrieved = populated_knowledge_store.get_document(doc_id)

        assert retrieved is not None
        assert retrieved.id == doc_id

    @pytest.mark.asyncio
    async def test_search_documents(self, populated_knowledge_store):
        """Test searching documents"""
        results = await populated_knowledge_store.search(
            query="multi-agent",
            max_results=5
        )

        assert len(results) > 0
        assert "multi-agent" in results[0].content.lower()

    @pytest.mark.asyncio
    async def test_get_by_source(self, populated_knowledge_store):
        """Test getting documents by source"""
        docs = populated_knowledge_store.get_by_source("test_agent")

        assert len(docs) > 0
        assert all(doc.source == "test_agent" for doc in docs)

    @pytest.mark.asyncio
    async def test_get_by_type(self, populated_knowledge_store):
        """Test getting documents by type"""
        from core.knowledge_store import DocumentType

        docs = populated_knowledge_store.get_by_type(
            DocumentType.RESEARCH_FINDING
        )

        assert len(docs) > 0
        assert all(
            doc.document_type == DocumentType.RESEARCH_FINDING
            for doc in docs
        )

    @pytest.mark.asyncio
    async def test_get_by_tag(self, populated_knowledge_store):
        """Test getting documents by tag"""
        docs = populated_knowledge_store.get_by_tag("ai")

        assert len(docs) > 0
        assert all("ai" in doc.tags for doc in docs)

    @pytest.mark.asyncio
    async def test_delete_document(self, populated_knowledge_store):
        """Test deleting a document"""
        docs = populated_knowledge_store.get_all()
        initial_count = len(docs)

        doc_id = docs[0].id
        result = populated_knowledge_store.delete_document(doc_id)

        assert result is True
        assert len(populated_knowledge_store.documents) == initial_count - 1

    @pytest.mark.asyncio
    async def test_update_document(self, populated_knowledge_store):
        """Test updating a document"""
        docs = populated_knowledge_store.get_all()
        doc_id = docs[0].id

        result = populated_knowledge_store.update_document(
            doc_id,
            content="Updated content",
            tags=["updated"]
        )

        assert result is True

        updated = populated_knowledge_store.get_document(doc_id)
        assert updated.content == "Updated content"
        assert "updated" in updated.tags

    @pytest.mark.asyncio
    async def test_statistics(self, populated_knowledge_store):
        """Test getting statistics"""
        stats = populated_knowledge_store.get_statistics()

        assert 'total_documents' in stats
        assert stats['total_documents'] > 0
        assert 'by_type' in stats
        assert 'by_source' in stats

    @pytest.mark.asyncio
    async def test_save_and_load(self, knowledge_store, temp_dir):
        """Test saving and loading"""
        from core.knowledge_store import DocumentType

        # Add a document
        await knowledge_store.add_document(
            content="Test save/load",
            source="test",
            document_type=DocumentType.RESEARCH_FINDING
        )

        # Save
        save_path = temp_dir / "test_save.json"
        knowledge_store.save(str(save_path))

        assert save_path.exists()

        # Create new store and load
        from core.knowledge_store import SimpleKnowledgeStore
        new_store = SimpleKnowledgeStore(
            persist_path=str(save_path),
            auto_save=False
        )
        new_store.load()

        assert len(new_store.documents) == 1

    @pytest.mark.asyncio
    async def test_export_markdown(self, populated_knowledge_store):
        """Test markdown export"""
        markdown = populated_knowledge_store.export_markdown()

        assert "# Knowledge Store Export" in markdown
        assert len(markdown) > 100


@pytest.mark.unit
class TestDocumentClass:
    """Test Document dataclass"""

    def test_document_creation(self):
        """Test creating a document"""
        from core.knowledge_store import Document, DocumentType
        from datetime import datetime

        doc = Document(
            id="test-id",
            content="Test content",
            document_type=DocumentType.RESEARCH_FINDING,
            source="test"
        )

        assert doc.id == "test-id"
        assert doc.content == "Test content"
        assert doc.document_type == DocumentType.RESEARCH_FINDING

    def test_document_to_dict(self):
        """Test document serialization"""
        from core.knowledge_store import Document, DocumentType

        doc = Document(
            id="test-id",
            content="Test content",
            document_type=DocumentType.RESEARCH_FINDING,
            source="test"
        )

        doc_dict = doc.to_dict()

        assert isinstance(doc_dict, dict)
        assert doc_dict['id'] == "test-id"
        assert doc_dict['document_type'] == "research_finding"
