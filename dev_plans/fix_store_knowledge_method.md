# Development Plan: Fix `_store_knowledge()` Method & Add Agent Tests

**Plan ID**: DEV-001
**Created**: 2025-01-13
**Priority**: 🔴 CRITICAL
**Status**: 📋 PLANNED
**Estimated Time**: 3-4 hours
**Risk Level**: Low (well-isolated bug fix)

---

## 📝 Executive Summary

Fix critical bug in `agents/base_agent.py::_store_knowledge()` method where required parameters (`source` and `document_type`) are missing when calling `knowledge_store.add_document()`. This causes runtime failures whenever agents attempt to store their research results.

**Impact**: Without this fix, all agent research workflows will fail.

---

## 🎯 Objectives

### Primary Goals
- [x] Fix `_store_knowledge()` to include all required parameters
- [x] Add missing `DocumentType` import to `base_agent.py`
- [x] Create comprehensive test suite for agent functionality
- [x] Achieve 90%+ test coverage for `base_agent.py`

### Secondary Goals
- [x] Add integration tests with real knowledge store
- [x] Document fix in code comments
- [x] Update conftest.py with reusable fixtures
- [x] Validate fix doesn't break existing functionality

---

## 🐛 Bug Analysis

### Current Issue

**File**: `agents/base_agent.py`
**Lines**: 86-96
**Severity**: CRITICAL - Runtime Error

```python
# CURRENT CODE (BROKEN)
async def _store_knowledge(self, result: Dict):
    """Store research result in knowledge base"""
    await self.knowledge_store.add_document(
        content=result["result"],
        # ❌ MISSING: source parameter
        # ❌ MISSING: document_type parameter
        metadata={
            "agent_id": self.agent_id,
            "role": self.role,
            "timestamp": result["timestamp"],
            "urls": result["urls"]
        }
    )
```

### Root Cause

The method signature of `knowledge_store.add_document()` requires:
1. `content` (str) - ✅ Provided
2. `source` (str) - ❌ **MISSING**
3. `document_type` (DocumentType) - ❌ **MISSING** (defaults to OTHER but should be AGENT_OUTPUT)

### Error That Would Occur

```python
TypeError: add_document() missing 1 required positional argument: 'source'
```

---

## 🔧 Implementation Plan

### Phase 1: Code Fixes (30 minutes)

#### Task 1.1: Add Missing Import
**File**: `agents/base_agent.py`
**Lines**: 1-6

```python
# BEFORE
from typing import List, Dict, Any, Optional
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime

# AFTER
from typing import List, Dict, Any, Optional
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
from core.knowledge_store import DocumentType  # ✅ ADD THIS LINE
```

**Checklist**:
- [ ] Add import statement
- [ ] Verify no circular import issues
- [ ] Run `python -m agents.base_agent` to check for import errors

---

#### Task 1.2: Fix `_store_knowledge()` Method
**File**: `agents/base_agent.py`
**Lines**: 86-96

```python
# BEFORE
async def _store_knowledge(self, result: Dict):
    """Store research result in knowledge base"""
    await self.knowledge_store.add_document(
        content=result["result"],
        metadata={
            "agent_id": self.agent_id,
            "role": self.role,
            "timestamp": result["timestamp"],
            "urls": result["urls"]
        }
    )

# AFTER
async def _store_knowledge(self, result: Dict) -> str:
    """
    Store research result in knowledge base

    Args:
        result: Dictionary containing task results with keys:
                - result: The actual content to store
                - agent_id: Source agent identifier
                - role: Agent role
                - timestamp: ISO format timestamp
                - urls: List of extracted URLs

    Returns:
        str: Document ID from knowledge store

    Raises:
        KeyError: If required keys missing from result dict
    """
    doc_id = await self.knowledge_store.add_document(
        content=result["result"],
        source=self.agent_id,                    # ✅ FIX: Add source
        document_type=DocumentType.AGENT_OUTPUT, # ✅ FIX: Add document type
        metadata={
            "agent_id": self.agent_id,
            "role": self.role,
            "timestamp": result["timestamp"],
            "urls": result["urls"]
        },
        tags=[self.role, "research"]             # ✅ ENHANCEMENT: Add tags
    )
    return doc_id  # ✅ ENHANCEMENT: Return doc_id for testing
```

**Changes Made**:
1. ✅ Added `source=self.agent_id` parameter
2. ✅ Added `document_type=DocumentType.AGENT_OUTPUT` parameter
3. ✅ Added `tags=[self.role, "research"]` for better categorization
4. ✅ Return `doc_id` for testing/verification
5. ✅ Enhanced docstring with full documentation
6. ✅ Added return type annotation

**Checklist**:
- [ ] Update method signature
- [ ] Add all required parameters
- [ ] Add return statement
- [ ] Update docstring
- [ ] Add type hints
- [ ] Verify indentation matches file style

---

#### Task 1.3: Update execute_task() Return Handling
**File**: `agents/base_agent.py`
**Lines**: 66

```python
# BEFORE
await self._store_knowledge(result)

# AFTER (optional enhancement)
doc_id = await self._store_knowledge(result)
result["knowledge_doc_id"] = doc_id  # Store doc_id in result for reference
```

**Checklist**:
- [ ] Optionally capture returned doc_id
- [ ] Store doc_id in result dict
- [ ] Test that execute_task still works

---

### Phase 2: Create Test Suite (2 hours)

#### Task 2.1: Create `tests/test_agents.py`
**File**: `tests/test_agents.py` (NEW FILE)
**Lines**: 0 → ~450

**Test Structure**:
```
tests/test_agents.py
├── TestResearchAgent (Unit Tests)
│   ├── test_agent_initialization
│   ├── test_execute_task_basic
│   ├── test_execute_task_with_context
│   ├── test_store_knowledge_called ⭐ CRITICAL TEST
│   ├── test_extract_urls
│   ├── test_extract_urls_none_found
│   ├── test_format_context_dict
│   ├── test_format_context_list
│   ├── test_memory_storage
│   ├── test_timestamp_format
│   └── test_urls_included_in_result
│
├── TestResearchAgentIntegration (Integration Tests)
│   ├── test_full_workflow ⭐ CRITICAL TEST
│   ├── test_multiple_tasks_storage
│   └── test_search_stored_knowledge
│
└── TestSpecificAgents (Agent Implementation Tests)
    ├── test_scholar_agent_system_prompt
    └── test_reporter_agent_system_prompt
```

**Key Test: `test_store_knowledge_called`**
```python
@pytest.mark.asyncio
async def test_store_knowledge_called(self, concrete_agent, mock_knowledge_store):
    """Test that _store_knowledge is called with correct parameters"""
    from core.knowledge_store import DocumentType

    task = "Test task"
    result = await concrete_agent.execute_task(task)

    # ⭐ VERIFY ALL REQUIRED PARAMETERS
    assert mock_knowledge_store.add_document.called

    call_kwargs = mock_knowledge_store.add_document.call_args[1]

    # Verify required parameters present
    assert "content" in call_kwargs
    assert "source" in call_kwargs              # ⭐ TESTS THE FIX
    assert "document_type" in call_kwargs       # ⭐ TESTS THE FIX

    # Verify parameter values
    assert call_kwargs["source"] == "test_agent_1"
    assert call_kwargs["document_type"] == DocumentType.AGENT_OUTPUT
```

**Checklist**:
- [ ] Create test file
- [ ] Add all fixtures (mock_llm, mock_knowledge_store, concrete_agent)
- [ ] Write 11 unit tests
- [ ] Write 3 integration tests
- [ ] Write 2 specific agent tests
- [ ] Ensure tests are isolated (no dependencies between tests)
- [ ] Add pytest markers (@pytest.mark.unit, @pytest.mark.integration)
- [ ] Test both success and error cases

---

#### Task 2.2: Update `tests/conftest.py`
**File**: `tests/conftest.py`
**Action**: ADD to existing file

```python
# ADD THESE FIXTURES TO conftest.py

@pytest.fixture
def mock_agent_llm():
    """Mock LLM for agent testing"""
    from unittest.mock import AsyncMock, Mock

    llm = AsyncMock()
    response = Mock()
    response.content = "Mock LLM response"
    llm.ainvoke = AsyncMock(return_value=response)
    return llm


@pytest.fixture
def test_agent(mock_agent_llm, knowledge_store):
    """Create a test agent instance"""
    from agents.base_agent import ResearchAgent

    class ConcreteTestAgent(ResearchAgent):
        def get_system_prompt(self) -> str:
            return "Test agent for testing purposes"

    return ConcreteTestAgent(
        agent_id="test_agent",
        role="tester",
        llm=mock_agent_llm,
        knowledge_store=knowledge_store
    )


@pytest.fixture
def populated_agent_store(knowledge_store):
    """Knowledge store with agent-generated documents"""
    import asyncio
    from core.knowledge_store import DocumentType

    async def populate():
        await knowledge_store.add_document(
            content="Agent research finding 1",
            source="test_agent",
            document_type=DocumentType.AGENT_OUTPUT,
            tags=["test", "research"]
        )
        await knowledge_store.add_document(
            content="Agent research finding 2",
            source="test_agent",
            document_type=DocumentType.AGENT_OUTPUT,
            tags=["test", "analysis"]
        )

    asyncio.run(populate())
    return knowledge_store
```

**Checklist**:
- [ ] Read existing conftest.py
- [ ] Add new fixtures without removing existing ones
- [ ] Verify fixtures work with existing tests
- [ ] Test fixture dependencies

---

### Phase 3: Testing & Validation (1 hour)

#### Task 3.1: Run Unit Tests
```bash
# Test only the new test file
pytest tests/test_agents.py -v

# Test with coverage
pytest tests/test_agents.py --cov=agents.base_agent --cov-report=term-missing

# Expected: 90%+ coverage for base_agent.py
```

**Checklist**:
- [ ] All unit tests pass (11/11)
- [ ] No test failures
- [ ] Coverage >= 90% for base_agent.py
- [ ] No warnings or deprecation notices

---

#### Task 3.2: Run Integration Tests
```bash
# Run integration tests
pytest tests/test_agents.py::TestResearchAgentIntegration -v

# Run with real knowledge store
pytest tests/test_agents.py -m integration
```

**Checklist**:
- [ ] All integration tests pass (3/3)
- [ ] Real knowledge store works correctly
- [ ] Documents are stored and retrievable
- [ ] No memory leaks

---

#### Task 3.3: Run Full Test Suite
```bash
# Run ALL tests to check for regressions
pytest

# Generate full coverage report
pytest --cov=cardinal_biggles --cov-report=html
```

**Checklist**:
- [ ] All existing tests still pass
- [ ] No regressions in other modules
- [ ] Overall coverage improved
- [ ] No new warnings

---

#### Task 3.4: Manual Verification
```python
# Create a test script: test_fix_manually.py
import asyncio
from agents.scholar import ScholarAgent
from core.knowledge_store import SimpleKnowledgeStore
from core.llm_factory import LLMFactory

async def test_manual():
    # Setup
    factory = LLMFactory("config/config.yaml")
    store = SimpleKnowledgeStore(persist_path=None, auto_save=False)

    # Create agent
    agent = ScholarAgent(
        agent_id="test_scholar",
        role="scholar",
        llm=factory.create_agent_llm("scholar"),
        knowledge_store=store
    )

    # Execute task
    result = await agent.execute_task("Test research task")

    # Verify storage worked
    docs = store.get_by_source("test_scholar")
    assert len(docs) == 1
    print("✅ Manual test passed!")
    print(f"Stored document: {docs[0].id}")

if __name__ == "__main__":
    asyncio.run(test_manual())
```

**Checklist**:
- [ ] Run manual test script
- [ ] Verify no exceptions raised
- [ ] Check document was stored correctly
- [ ] Verify document has correct DocumentType

---

### Phase 4: Documentation & Cleanup (30 minutes)

#### Task 4.1: Update Code Comments
**File**: `agents/base_agent.py`

```python
# Add comment above _store_knowledge method
# Fixed: 2025-01-13 - Added missing source and document_type parameters
# See: dev_plans/fix_store_knowledge_method.md
```

**Checklist**:
- [ ] Add fix reference comment
- [ ] Update method docstring
- [ ] Add inline comments for key parameters

---

#### Task 4.2: Update Documentation
**Files to Update**:
- `CLAUDE.md` - Update line 86-96 example
- `AI_ASSISTANT_GUIDE.md` - No changes needed
- `SPECIFICATION.md` - No changes needed

**Checklist**:
- [ ] Update CLAUDE.md with correct code
- [ ] Verify all line number references are correct
- [ ] Check for any other references to _store_knowledge

---

#### Task 4.3: Create Changelog Entry
**File**: `CHANGELOG.md` (create if doesn't exist)

```markdown
# Changelog

## [Unreleased]

### Fixed
- **CRITICAL**: Fixed missing parameters in `base_agent._store_knowledge()` method
  - Added required `source` parameter
  - Added required `document_type` parameter set to `DocumentType.AGENT_OUTPUT`
  - Added `tags` for better categorization
  - Method now returns document ID for verification
  - See: dev_plans/fix_store_knowledge_method.md

### Added
- Comprehensive test suite for agent functionality (16 tests)
- Integration tests with real knowledge store
- Agent fixtures in conftest.py
- Documentation for _store_knowledge method
```

**Checklist**:
- [ ] Create or update CHANGELOG.md
- [ ] Document all changes
- [ ] Include test additions
- [ ] Reference this dev plan

---

## 📋 Master Checklist

### Pre-Implementation
- [x] Review current code
- [x] Identify root cause
- [x] Create development plan
- [x] Get stakeholder approval (if needed)

### Implementation - Phase 1: Code Fixes
- [ ] Add DocumentType import to base_agent.py
- [ ] Fix _store_knowledge() method parameters
- [ ] Add return statement for doc_id
- [ ] Update docstrings
- [ ] Add type hints
- [ ] Optional: Update execute_task to capture doc_id

### Implementation - Phase 2: Tests
- [ ] Create tests/test_agents.py
- [ ] Write 11 unit tests for ResearchAgent
- [ ] Write 3 integration tests
- [ ] Write 2 specific agent tests
- [ ] Update conftest.py with fixtures
- [ ] Ensure all tests are isolated

### Implementation - Phase 3: Validation
- [ ] Run unit tests (expect 11 passed)
- [ ] Verify 90%+ coverage for base_agent.py
- [ ] Run integration tests (expect 3 passed)
- [ ] Run full test suite (no regressions)
- [ ] Manual verification with test script
- [ ] Check no exceptions in real usage

### Implementation - Phase 4: Documentation
- [ ] Add code comments referencing fix
- [ ] Update CLAUDE.md if needed
- [ ] Create/update CHANGELOG.md
- [ ] Update this plan status to "COMPLETED"

### Post-Implementation
- [ ] Code review (if team process requires)
- [ ] Commit changes with descriptive message
- [ ] Update GitHub issues (if applicable)
- [ ] Announce fix to team

---

## 🎯 Success Criteria

### Must Have (Required)
1. ✅ `_store_knowledge()` includes all required parameters
2. ✅ No runtime errors when agents store knowledge
3. ✅ All new tests pass (16/16)
4. ✅ Test coverage >= 90% for base_agent.py
5. ✅ No regressions in existing tests

### Nice to Have (Optional)
1. ✅ Return doc_id for verification
2. ✅ Add tags for better categorization
3. ✅ Enhanced docstrings
4. ✅ Manual test script
5. ✅ CHANGELOG entry

---

## 🧪 Test Plan Details

### Test Coverage Matrix

| Component | Test Type | Test Name | Coverage |
|-----------|-----------|-----------|----------|
| Agent Init | Unit | test_agent_initialization | Constructor |
| execute_task | Unit | test_execute_task_basic | Basic flow |
| execute_task | Unit | test_execute_task_with_context | With context |
| _store_knowledge | Unit | test_store_knowledge_called | ⭐ FIX VERIFICATION |
| _extract_urls | Unit | test_extract_urls | URL extraction |
| _extract_urls | Unit | test_extract_urls_none_found | Edge case |
| _format_context | Unit | test_format_context_dict | Dict formatting |
| _format_context | Unit | test_format_context_list | List formatting |
| Memory | Unit | test_memory_storage | Memory tracking |
| Timestamp | Unit | test_timestamp_format | ISO format |
| URLs | Unit | test_urls_included_in_result | URL inclusion |
| Full Flow | Integration | test_full_workflow | End-to-end |
| Multiple Tasks | Integration | test_multiple_tasks_storage | Batch storage |
| Search | Integration | test_search_stored_knowledge | Retrieval |
| ScholarAgent | Unit | test_scholar_agent_system_prompt | Prompt check |
| ReporterAgent | Unit | test_reporter_agent_system_prompt | Prompt check |

**Total Tests**: 16
**Critical Tests**: 2 (marked with ⭐)

---

## 🚨 Risk Assessment

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing functionality | Low | High | Run full test suite |
| Import circular dependency | Low | Medium | Test import in isolation |
| Test fixtures conflict | Low | Low | Isolated test fixtures |
| Coverage not achieved | Low | Low | Add more edge case tests |
| Integration test failures | Low | Medium | Test with real store first |

### Rollback Plan

If issues arise after deployment:

1. **Immediate**: Revert commit
   ```bash
   git revert <commit-hash>
   ```

2. **Alternative**: Add try/except wrapper
   ```python
   try:
       doc_id = await self.knowledge_store.add_document(...)
   except TypeError:
       # Fallback for old signature
       doc_id = await self.knowledge_store.add_document(
           content=result["result"],
           metadata={...}
       )
   ```

---

## 📊 Expected Outcomes

### Before Fix
```python
# Runtime Error
TypeError: add_document() missing 1 required positional argument: 'source'

# Test Coverage
agents/base_agent.py: 0% coverage
```

### After Fix
```python
# Success
✅ Document stored successfully
✅ doc_id: "abc-123-def-456"
✅ Document type: AGENT_OUTPUT
✅ Source: test_agent_1

# Test Coverage
agents/base_agent.py: 92% coverage (11/12 functions)
Missing: Abstract methods only
```

---

## 🔍 Code Review Checklist

### For Reviewer
- [ ] Import statement added correctly
- [ ] All required parameters present
- [ ] Return type matches signature
- [ ] Docstring is comprehensive
- [ ] Tests are well-structured
- [ ] Tests cover edge cases
- [ ] No code duplication
- [ ] Follows project style guide
- [ ] No security issues
- [ ] Documentation updated

---

## 📝 Commit Message Template

```
fix(agents): Add missing parameters to _store_knowledge method

BREAKING: This fixes a critical bug where agents couldn't store knowledge
due to missing required parameters.

Changes:
- Add 'source' parameter to knowledge_store.add_document() call
- Add 'document_type' parameter (set to AGENT_OUTPUT)
- Add 'tags' for better categorization
- Return doc_id for verification
- Add DocumentType import

Tests:
- Add 16 comprehensive tests for agent functionality
- Achieve 92% coverage for base_agent.py
- Add integration tests with real knowledge store
- Update conftest.py with agent fixtures

See: dev_plans/fix_store_knowledge_method.md

Fixes: #<issue-number>
```

---

## 📚 References

### Related Files
- `agents/base_agent.py` - Main fix location
- `core/knowledge_store.py` - Method signature definition
- `tests/test_agents.py` - New test file
- `tests/conftest.py` - Fixture updates
- `CLAUDE.md` - Documentation reference

### Related Issues
- Documentation comparison report (this session)
- Missing test coverage for agents
- Knowledge store integration

### Documentation
- LangChain async patterns
- pytest-asyncio usage
- Python dataclasses and enums

---

## ✅ Sign-Off

### Developer
- Name: ___________________
- Date: ___________________
- Signature: ___________________

### Code Reviewer (if applicable)
- Name: ___________________
- Date: ___________________
- Signature: ___________________

---

## 📅 Timeline

| Phase | Duration | Start | End | Status |
|-------|----------|-------|-----|--------|
| Planning | 30 min | - | - | ✅ COMPLETE |
| Code Fixes | 30 min | - | - | 📋 PENDING |
| Test Creation | 2 hours | - | - | 📋 PENDING |
| Validation | 1 hour | - | - | 📋 PENDING |
| Documentation | 30 min | - | - | 📋 PENDING |
| **TOTAL** | **4 hours** | - | - | 📋 PLANNED |

---

## 🎉 Completion Criteria

This plan is considered complete when:

1. ✅ All code changes implemented
2. ✅ All 16 tests passing
3. ✅ Coverage >= 90% for base_agent.py
4. ✅ No regressions in existing tests
5. ✅ Documentation updated
6. ✅ Code committed with proper message
7. ✅ This plan marked as COMPLETED

---

**End of Development Plan**

*Last Updated: 2025-01-13*
*Plan Status: 📋 READY FOR IMPLEMENTATION*
