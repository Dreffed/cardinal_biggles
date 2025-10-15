# Linting & Code Quality Guide

This guide covers code quality tools and linting configuration for Cardinal Biggles.

## Overview

Cardinal Biggles uses multiple linting tools to maintain code quality:

- **Python**: black, isort, flake8, bandit
- **Markdown**: markdownlint
- **YAML**: yamllint (via pre-commit)
- **Pre-commit hooks**: Automated checks before commits

---

## Quick Start

```bash
# Complete setup
make dev-setup

# Or step by step:
pip install -r requirements-dev.txt
npm install
make setup-hooks
```

---

## Python Linting

### Black (Code Formatter)

**Purpose:** Automatic code formatting

**Configuration:** `pyproject.toml`

```bash
# Format all Python files
black . --line-length=100

# Check without modifying
black . --check

# Or use Make
make format
```

**Rules:**
- Line length: 100 characters
- String quotes: Double quotes preferred
- Indentation: 4 spaces

### isort (Import Sorting)

**Purpose:** Organize Python imports

```bash
# Sort imports
isort . --profile black --line-length 100

# Check only
isort . --check-only
```

**Configuration:**
```toml
[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
```

### Flake8 (Linting)

**Purpose:** Check Python code style and quality

```bash
# Run flake8
flake8 . --max-line-length=100 --extend-ignore=E203,W503

# Or use Make
make lint
```

**Ignored Rules:**
- `E203`: Whitespace before ':' (conflicts with black)
- `W503`: Line break before binary operator (conflicts with black)

### Bandit (Security)

**Purpose:** Find security issues in Python code

```bash
# Run bandit
bandit -r . -c pyproject.toml

# Specific directory
bandit -r core/
```

**Configuration:** `pyproject.toml`

---

## Markdown Linting

### markdownlint-cli

**Purpose:** Enforce consistent Markdown style

**Configuration:** `.markdownlint.json`

```bash
# Lint all markdown files
npm run lint:md

# Auto-fix issues
npm run lint:md:fix

# Or use Make
make lint-md
make lint-md-fix
```

### Configuration Rules

```json
{
  "default": true,
  "MD003": { "style": "atx" },           // Heading style: # Heading
  "MD007": { "indent": 2 },              // Unordered list indent: 2 spaces
  "MD013": {                             // Line length
    "line_length": 120,
    "code_blocks": false,
    "tables": false
  },
  "MD024": { "siblings_only": true },   // Duplicate headings in siblings only
  "MD033": false,                        // Allow inline HTML
  "MD041": false,                        // First line doesn't need to be heading
  "MD046": { "style": "fenced" }        // Code block style: ```
}
```

### Common Markdown Rules

| Rule | Description | Fix |
|------|-------------|-----|
| MD001 | Heading levels increment by one | Don't skip heading levels |
| MD003 | Heading style | Use `# Heading` not `Heading\n===` |
| MD009 | Trailing spaces | Remove trailing whitespace |
| MD012 | Multiple consecutive blank lines | Use single blank lines |
| MD022 | Headings surrounded by blank lines | Add blank lines around headings |
| MD025 | Single top-level heading | Only one `# Heading` per file |
| MD031 | Fenced code blocks surrounded by blank lines | Add blank lines around code blocks |
| MD032 | Lists surrounded by blank lines | Add blank lines around lists |

### Ignoring Files

Edit `.markdownlintignore`:

```
# Ignore generated files
reports/
logs/

# Ignore specific files
CHANGELOG.md
```

---

## Pre-commit Hooks

### Setup

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Or use Make
make setup-hooks
```

### Manual Run

```bash
# Run all hooks
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run markdownlint --all-files

# Or use Make
make pre-commit
```

### Hook Configuration

File: `.pre-commit-config.yaml`

**Hooks included:**
1. **black** - Python formatting
2. **isort** - Import sorting
3. **flake8** - Python linting
4. **markdownlint** - Markdown linting
5. **check-yaml** - YAML syntax validation
6. **check-json** - JSON syntax validation
7. **trailing-whitespace** - Remove trailing spaces
8. **end-of-file-fixer** - Ensure files end with newline
9. **check-added-large-files** - Prevent large file commits
10. **detect-private-key** - Detect accidentally committed keys
11. **bandit** - Security checks

### Skipping Hooks

```bash
# Skip all hooks for one commit
git commit --no-verify

# Skip specific hook
SKIP=flake8 git commit -m "message"
```

---

## Make Commands

### Linting Commands

```bash
make lint           # Run all linters
make lint-fix       # Run with auto-fix
make lint-md        # Markdown only
make lint-md-fix    # Fix markdown issues
```

### Testing Commands

```bash
make test           # Run all tests
make test-cov       # With coverage report
make test-unit      # Unit tests only
make test-integration  # Integration tests only
```

### Formatting Commands

```bash
make format         # Format Python code
make clean          # Clean generated files
```

### Setup Commands

```bash
make install        # Install Python deps
make install-node   # Install Node.js deps
make setup-hooks    # Setup pre-commit
make dev-setup      # Complete dev setup
```

---

## IDE Integration

### VS Code

**Install Extensions:**
- Python (Microsoft)
- Pylance
- Black Formatter
- isort
- markdownlint

**Settings (`.vscode/settings.json`):**

```json
{
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=100",
    "--extend-ignore=E203,W503"
  ],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": [
    "--line-length=100"
  ],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "markdownlint.config": {
    "extends": ".markdownlint.json"
  },
  "[markdown]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "DavidAnson.vscode-markdownlint"
  }
}
```

### PyCharm

**Enable Tools:**
1. Preferences → Tools → Black
   - On save: Yes
   - Arguments: `--line-length=100`

2. Preferences → Tools → File Watchers
   - Add: isort
   - Arguments: `$FilePath$ --profile black`

3. Preferences → Editor → Inspections
   - Enable: Flake8
   - Configure: Add arguments `--max-line-length=100`

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
          npm install

      - name: Run Python linters
        run: |
          black . --check
          isort . --check-only
          flake8 .

      - name: Run markdown linter
        run: npm run lint:md

      - name: Run security checks
        run: bandit -r . -c pyproject.toml
```

---

## Troubleshooting

### Black and Flake8 Conflicts

**Problem:** Flake8 complains about formatting that Black enforces

**Solution:** Add these to flake8 ignore list:
```
E203: Whitespace before ':'
W503: Line break before binary operator
```

### isort and Black Conflicts

**Problem:** isort and Black format imports differently

**Solution:** Use `--profile black` with isort:
```bash
isort . --profile black
```

### Markdown Line Length

**Problem:** Long lines in code blocks or tables

**Solution:** Disable for those elements:
```json
{
  "MD013": {
    "code_blocks": false,
    "tables": false
  }
}
```

### Pre-commit Hook Fails

**Problem:** Hook fails but file looks correct

**Solution:**
```bash
# Update hooks
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall
pre-commit uninstall
pre-commit install
```

---

## Best Practices

### Before Committing

1. Run formatters:
   ```bash
   make format
   ```

2. Run linters:
   ```bash
   make lint
   ```

3. Fix any issues:
   ```bash
   make lint-fix
   ```

4. Run tests:
   ```bash
   make test
   ```

### Writing Good Markdown

1. **Use ATX-style headers:**
   ```markdown
   # Good
   ## Good

   Bad
   ===
   ```

2. **Add blank lines around blocks:**
   ```markdown
   Text before.

   ```code
   code block
   ```

   Text after.
   ```

3. **Consistent list style:**
   ```markdown
   - Item 1
   - Item 2
     - Nested item (2 spaces)
   ```

4. **Keep lines under 120 characters** (except code/tables)

### Python Code Style

1. **Line length: 100 characters**
2. **Use double quotes for strings**
3. **Docstrings for all public functions**
4. **Type hints where appropriate**
5. **Organize imports:**
   - Standard library
   - Third-party
   - Local imports

---

## Configuration Files Summary

| File | Purpose |
|------|---------|
| `.markdownlint.json` | Markdown linting rules |
| `.markdownlintignore` | Files to ignore for markdown |
| `.pre-commit-config.yaml` | Pre-commit hook configuration |
| `pyproject.toml` | Python tool configuration |
| `package.json` | Node.js scripts and dependencies |
| `Makefile` | Development commands |

---

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [pre-commit Documentation](https://pre-commit.com/)

---

**Last Updated:** 2025-01-14
