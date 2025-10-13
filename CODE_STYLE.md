# Cardinal Biggles - Code Style Guide

## Python Style

### Base Standard

- **PEP 8**: Follow Python Enhancement Proposal 8
- **PEP 484**: Type hints for all functions
- **PEP 257**: Docstring conventions

### Formatting

- **Line Length**: 100 characters
- **Indentation**: 4 spaces (no tabs)
- **String Quotes**: Double for docstrings, single for code
- **Imports**: Sorted with isort

### Tools

```bash
black cardinal_biggles/ --line-length 100
isort cardinal_biggles/
mypy cardinal_biggles/
flake8 cardinal_biggles/ --max-line-length=100
```

## Naming Conventions

```python
# Classes: PascalCase
class ResearchAgent:
    pass

# Functions: snake_case
def execute_task():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private: _leading_underscore
def _internal_method():
    pass
```

## Import Organization

```python
# 1. Standard library
import asyncio
import os
from typing import Dict, List, Optional

# 2. Third-party
import aiohttp
import pytest

# 3. Local
from agents.base_agent import ResearchAgent
from core.llm_factory import LLMFactory
```

## Type Hints

```python
def function(
    param1: str,
    param2: int,
    param3: Optional[Dict[str, Any]] = None
) -> List[Result]:
    pass
```

## Async Patterns

```python
# Always async for I/O
async def fetch_data() -> Data:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Parallel execution
results = await asyncio.gather(task1(), task2(), task3())
```

## Error Handling

```python
try:
    result = await api_call()
except aiohttp.ClientError as e:
    logger.error(f"Network error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected: {e}", exc_info=True)
    raise
```

## Documentation

```python
class Example:
    """
    Brief description.

    Longer description with details.

    Attributes:
        attr1: Description
        attr2: Description

    Example:
        obj = Example(param)
        result = obj.method()
    """

    def method(self, param: str) -> int:
        """
        Brief description.

        Args:
            param: Description

        Returns:
            Description of return

        Raises:
            ValueError: When invalid
        """
        pass
```

## Comments

```python
# Use comments to explain "why", not "what"

# GOOD - Explains reasoning
# Use exponential backoff to avoid overwhelming API
await asyncio.sleep(2 ** retry_count)

# BAD - States the obvious
# Sleep for 2 to the power of retry_count
await asyncio.sleep(2 ** retry_count)
```
