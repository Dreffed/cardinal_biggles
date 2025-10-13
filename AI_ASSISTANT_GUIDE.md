# AI Assistant Guide for Cardinal Biggles Development

**For**: Claude Code, GitHub Copilot, Cursor, and other AI coding assistants
**Purpose**: Guidelines for effective contribution to Cardinal Biggles

---

## Quick Start for AI Assistants

### When Starting a Task

1. **Read these files first**:
   - SPECIFICATION.md - Technical details
   - ARCHITECTURE.md - System design
   - CODE_STYLE.md - Coding standards
   - This file - AI-specific guidelines

2. **Understand the context**:
   - What component are you working on?
   - Which agents/tools does it interact with?
   - What are the performance requirements?

3. **Check existing patterns**:
   - Look at similar components
   - Follow naming conventions
   - Reuse existing utilities

---

## Core Principles

### 1. Async-First

- All I/O operations MUST be async
- Use `async def` and `await`
- Never use blocking calls

```python
# CORRECT
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        return await response.json()

# WRONG
async def fetch_data():
    response = requests.get(url)  # Blocking!
    return response.json()
```

### 2. Type Hints Always

- All function signatures must have type hints
- Use Optional for nullable types

```python
# CORRECT
async def search(
    query: str,
    max_results: int = 10,
    filters: Optional[Dict[str, Any]] = None
) -> List[SearchResult]:
    pass

# WRONG
async def search(query, max_results=10):
    pass
```

### 3. Error Handling

- Use try/except for all external calls
- Log errors with context
- Provide meaningful error messages

```python
# CORRECT
try:
    result = await llm.ainvoke(messages)
except Exception as e:
    logger.error(f"LLM invocation failed for {self.agent_id}: {e}")
    raise LLMProviderError(f"Failed: {e}") from e

# WRONG
result = await llm.ainvoke(messages)  # No error handling
```

### 4. Logging

- Use structured logging
- Include context
- Appropriate log levels

```python
# CORRECT
logger.info(f"Agent {self.agent_id} starting task")
logger.debug(f"Context: {context.keys()}")
logger.error(f"Task failed: {error}", exc_info=True)

# WRONG
print(f"Starting task")  # Don't use print
```

---

## Component-Specific Guidelines

### Working on Agents

**When creating a new agent**:

```python
from agents.base_agent import ResearchAgent

class NewAgent(ResearchAgent):
    def get_system_prompt(self) -> str:
        return """You are a NewAgent specialized in X.

        Your responsibilities:
        1. Task A
        2. Task B

        Output format:
        - Field 1
        - Field 2
        """

    async def research_specific(self, topic: str) -> Dict:
        task = f"Research {topic}"
        return await self.execute_task(task)
```

### Working on Tools

**When creating a new tool**:

```python
class NewTool:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def execute(self, param: str, **kwargs) -> Any:
        logger.info(f"Executing NewTool with {param}")
        try:
            result = await self._do_work(param)
            return result
        except Exception as e:
            logger.error(f"NewTool failed: {e}")
            raise
```

---

## Testing Guidelines

### Test Structure

```python
@pytest.mark.unit
class TestComponentName:
    """Test suite for ComponentName"""

    def test_component_does_expected_thing(self, fixtures):
        """
        Test that component does expected thing.

        Given: Initial state
        When: Action performed
        Then: Expected outcome
        """
        # Arrange
        component = Component(config)

        # Act
        result = component.method()

        # Assert
        assert result == expected
```

### When to Mock

**Mock external services**:

- API calls (OpenAI, Claude, Perplexity)
- Web requests
- File system operations (sometimes)

**Don't mock internal logic**:

- Configuration parsing
- Data transformations
- Utility functions

---

## Common Mistakes to Avoid

### Mistake 1: Mixing Sync and Async

```python
# WRONG
async def process():
    data = fetch_data()  # Synchronous!

# CORRECT
async def process():
    data = await fetch_data_async()
```

### Mistake 2: Not Handling None

```python
# WRONG
def get_value(key: str) -> str:
    return config[key]  # KeyError if missing!

# CORRECT
def get_value(key: str) -> Optional[str]:
    return config.get(key)
```

### Mistake 3: Hardcoded Values

```python
# WRONG
llm = ChatOpenAI(model="gpt-4")  # Hardcoded!

# CORRECT
llm = self.llm_factory.create_agent_llm(self.agent_id)
```

### Mistake 4: Missing Docstrings

```python
# WRONG
async def execute_task(self, task):
    pass

# CORRECT
async def execute_task(self, task_description: str) -> Dict[str, Any]:
    """
    Execute a research task.

    Args:
        task_description: Clear description of the task

    Returns:
        Dict containing task results
    """
    pass
```

---

## Code Review Checklist

Before submitting code:

- [ ] All functions have type hints
- [ ] All async functions use async/await
- [ ] All public functions have docstrings
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Tests are included (90%+ coverage)
- [ ] No hardcoded values
- [ ] Follows existing patterns
- [ ] Configuration is in config.yaml
- [ ] No security issues

---

## Quick Reference

### File Locations

```text
agents/          - All agent implementations
core/            - Core system components
tools/           - Utility tools
config/          - Configuration files
tests/           - All tests
```

### Common Commands

```bash
pytest                                    # Run all tests
pytest tests/test_file.py                # Run specific test
pytest --cov=cardinal_biggles            # Run with coverage
black cardinal_biggles/                  # Format code
mypy cardinal_biggles/                   # Type check
```

---

## When Stuck

1. Check existing similar code
2. Read the specification
3. Check tests
4. Enable debug logging
5. Ask for clarification

---
