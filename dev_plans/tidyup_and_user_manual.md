# Development Plan: Tidy Up Files & Create User Manual

**Plan ID**: DEV-004
**Created**: 2025-10-14
**Priority**: 🟢 MEDIUM (Documentation & Organization)
**Status**: 📋 PLANNED
**Estimated Time**: 2-3 hours
**Risk Level**: Low (documentation and organization)

---

## 📝 Executive Summary

Clean up the project structure, remove temporary files, organize documentation, and create a comprehensive user manual that serves as the primary guide for Cardinal Biggles users.

**Impact**:
- **User Experience**: Clear, comprehensive documentation
- **Project Organization**: Clean file structure
- **Maintenance**: Easier to navigate and update
- **Onboarding**: Faster learning curve for new users

---

## 🎯 Objectives

### Primary Goals
- [ ] Identify and remove temporary/duplicate files
- [ ] Organize project directory structure
- [ ] Create comprehensive `docs/USER_MANUAL.md`
- [ ] Update cross-references between documentation files
- [ ] Clean up test artifacts
- [ ] Verify all documentation is accurate

### Secondary Goals
- [ ] Create documentation index/navigation
- [ ] Add quick reference guide
- [ ] Create troubleshooting flowcharts
- [ ] Add usage examples for common scenarios
- [ ] Create FAQ section

---

## 🔍 Current State Analysis

### File Inventory

#### Documentation Files (Current)
```
./
├── README.md                    # Main project README
├── CLAUDE.md                    # Claude-specific documentation
└── docs/
    ├── LOCAL_SETUP.md           # Local Ollama setup guide
    └── ARCHITECTURE.md          # (assumed to exist)
```

#### Test/Temporary Files to Review
```
./
├── test_llm_factory.py          # Root-level test file (should be in tests/)
├── reports/local/               # Test reports
│   ├── smoke_test.md            # Keep as reference
│   ├── *.json                   # Intermediate results (cleanup?)
│   └── history_of_timezones_*   # Old test files (cleanup)
└── logs/                        # Log files (review and cleanup)
```

#### Scripts
```
scripts/
├── setup_local_models.sh        # Setup script
├── setup_local_models.bat       # Setup script (Windows)
├── smoke_test_local.sh          # Smoke test
├── smoke_test_local.bat         # Smoke test (Windows)
└── quick_test_local.sh          # Quick test
```

#### Development Plans
```
dev_plans/
├── fix_cli_and_add_hil.md                    # Completed plan
├── ollama_local_config_and_smoke_test.md     # Completed plan
└── tidyup_and_user_manual.md                 # This file
```

---

## 📋 File Cleanup Tasks

### Phase 1: Identify Files for Cleanup (20 minutes)

#### Task 1.1: Review Test Files

**Files to Review**:
```bash
# Root-level test file (move to tests/)
./test_llm_factory.py

# Old test reports (archive or delete)
./reports/local/history_of_timezones_and_daylight_savings_*.json
./reports/local/history_of_timezones_and_daylight_savings_*.md

# Keep these (recent smoke test)
./reports/local/smoke_test.md
./reports/local/machine_learning_*.json
```

**Actions**:
- [ ] Move `test_llm_factory.py` to `tests/` directory
- [ ] Archive or delete old test reports (history_of_timezones_*)
- [ ] Keep recent smoke test files as reference

#### Task 1.2: Review Log Files

**Files to Review**:
```bash
./logs/*.log
```

**Actions**:
- [ ] Review log files for size
- [ ] Keep recent logs (last 7 days)
- [ ] Archive or delete old logs
- [ ] Add `.gitignore` entry for `logs/*.log` if not present

#### Task 1.3: Review Python Cache Files

**Files to Check**:
```bash
**/__pycache__/
**/*.pyc
**/*.pyo
**/.pytest_cache/
```

**Actions**:
- [ ] Verify `.gitignore` includes Python cache entries
- [ ] Clean up any committed cache files

#### Task 1.4: Review Configuration Files

**Files to Check**:
```bash
.env
.env.example
config/*.yaml
```

**Actions**:
- [ ] Verify `.env` is in `.gitignore`
- [ ] Ensure `.env.example` exists with all required variables
- [ ] Verify all config files are properly documented

---

### Phase 2: Organize Directory Structure (30 minutes)

#### Task 2.1: Create Missing Directories

**Directories to Ensure Exist**:
```bash
./docs/          # Documentation
./reports/       # Generated reports
./logs/          # Log files
./data/          # Knowledge store persistence
./tests/         # Test files
./scripts/       # Utility scripts
./config/        # Configuration files
./dev_plans/     # Development plans
```

**Actions**:
- [ ] Create any missing directories
- [ ] Add `.gitkeep` files to track empty directories
- [ ] Add appropriate `.gitignore` entries

#### Task 2.2: Create Documentation Index

**File**: `docs/README.md` (NEW)

```markdown
# Cardinal Biggles Documentation

## Getting Started
- [User Manual](USER_MANUAL.md) - Complete guide for users
- [Quick Start](../README.md#quick-start) - Get running in 5 minutes
- [Local Setup](LOCAL_SETUP.md) - Run without API keys

## Configuration
- [Configuration Guide](USER_MANUAL.md#configuration) - Detailed config options
- [Local Mode](LOCAL_SETUP.md) - Ollama-only setup
- [Multi-Provider Setup](USER_MANUAL.md#multi-provider-setup) - Cloud providers

## Advanced Topics
- [Architecture](ARCHITECTURE.md) - System design
- [Human-in-the-Loop](USER_MANUAL.md#human-in-the-loop) - Interactive workflow
- [Development Guide](../CLAUDE.md) - For contributors

## Troubleshooting
- [Common Issues](USER_MANUAL.md#troubleshooting) - Solutions to common problems
- [FAQ](USER_MANUAL.md#faq) - Frequently asked questions

## Reference
- [CLI Reference](USER_MANUAL.md#cli-reference) - Command-line interface
- [API Reference](ARCHITECTURE.md) - Internal APIs
- [Configuration Schema](USER_MANUAL.md#configuration-schema) - Config file structure
```

#### Task 2.3: Update .gitignore

**File**: `.gitignore` (UPDATE)

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment Variables
.env
.env.local

# Logs
logs/*.log
*.log

# Reports (keep examples, ignore generated)
reports/*
!reports/.gitkeep
!reports/local/smoke_test.md

# Data
data/*
!data/.gitkeep

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# OS
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
*.bak
```

---

## 📚 User Manual Creation (90 minutes)

### Phase 3: Create Comprehensive User Manual

#### Task 3.1: Define User Manual Structure

**File**: `docs/USER_MANUAL.md` (NEW)

**Table of Contents**:
```markdown
# Cardinal Biggles User Manual

## Table of Contents

### Part 1: Getting Started
1. Introduction
2. What is Cardinal Biggles?
3. Key Features
4. Quick Start
5. Installation
6. First Research Project

### Part 2: Core Concepts
7. Multi-Agent Architecture
8. LLM Providers
9. Research Workflow
10. Knowledge Store
11. Report Generation

### Part 3: Configuration
12. Configuration Overview
13. LLM Provider Configuration
14. Agent Configuration
15. Research Parameters
16. Output Configuration
17. Logging Configuration

### Part 4: Using Cardinal Biggles
18. CLI Commands
19. Running Research
20. Local Mode (No API Keys)
21. Cloud Mode (API Keys)
22. Hybrid Mode (Mixed Providers)
23. Human-in-the-Loop Mode

### Part 5: Advanced Topics
24. Custom Agents
25. Provider Fallbacks
26. Performance Optimization
27. Cost Management
28. Batch Processing
29. Integration with Other Tools

### Part 6: Troubleshooting
30. Common Issues
31. Error Messages
32. Performance Problems
33. Provider-Specific Issues
34. FAQ

### Part 7: Reference
35. CLI Reference
36. Configuration Schema
37. Environment Variables
38. Output Formats
39. Glossary

### Part 8: Appendices
40. Example Configurations
41. Use Case Examples
42. Best Practices
43. Changelog
```

#### Task 3.2: Write User Manual Content

**Part 1: Getting Started** (20 minutes)

```markdown
# Cardinal Biggles User Manual

**Version**: 0.2.0
**Last Updated**: 2025-10-14

---

## Part 1: Getting Started

### 1. Introduction

Welcome to Cardinal Biggles! This user manual is your comprehensive guide to using the multi-agent research orchestration system.

**Who Should Use This Manual**:
- Researchers conducting market analysis
- Business analysts exploring trends
- Product managers researching competitors
- Developers integrating Cardinal Biggles
- Anyone needing comprehensive research reports

**What You'll Learn**:
- How to install and configure Cardinal Biggles
- How to run research workflows
- How to customize agent behavior
- How to optimize performance and cost
- How to troubleshoot common issues

### 2. What is Cardinal Biggles?

Cardinal Biggles is an AI-powered research orchestration system that uses specialized agents to conduct comprehensive research on any topic. It combines multiple LLM providers (Ollama, OpenAI, Claude, Perplexity) to deliver high-quality, well-cited research reports.

**Key Capabilities**:
- Multi-agent architecture with specialized roles
- Support for multiple LLM providers
- Intelligent web search with citation tracking
- Human-in-the-loop review checkpoints
- Comprehensive markdown reports with references
- Local-only mode (no API keys required)

### 3. Key Features

**Multi-Agent Research**:
- 🎯 **Coordinator**: Orchestrates the workflow
- 📊 **Trend Scout**: Identifies market trends
- 📜 **Historian**: Researches historical context
- 🎓 **Scholar**: Analyzes academic papers
- 📰 **Journalist**: Reviews news articles
- 📚 **Bibliophile**: Researches books
- 📝 **Reporter**: Generates final reports

**Flexible LLM Support**:
- Local models (Ollama) - Free, private
- OpenAI (GPT-4, GPT-3.5) - Fast, reliable
- Anthropic Claude - Excellent analysis
- Perplexity - Built-in web search

**Human-in-the-Loop**:
- Review agent outputs at key checkpoints
- Approve, edit, or regenerate results
- Quality control before expensive operations
- Iterative refinement

### 4. Quick Start

Get running in 5 minutes:

**Option 1: Local Mode (No API Keys)**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.1:8b

# Run research
python -m cli.main research "AI Trends" --config config/local_ollama.yaml
```

**Option 2: Cloud Mode (With API Keys)**
```bash
# Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export PERPLEXITY_API_KEY="pplx-..."

# Run research
python -m cli.main research "AI Trends"
```

### 5. Installation

**Prerequisites**:
- Python 3.9 or higher
- pip (Python package installer)
- Git (for cloning repository)
- 8GB+ RAM (for local models)

**Step-by-Step Installation**:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Dreffed/cardinal_biggles.git
   cd cardinal_biggles
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Installation**
   ```bash
   python -m cli.main --help
   ```

5. **Setup Configuration** (Choose one)

   **For Local Mode**:
   ```bash
   # Use existing local config
   cp config/local_ollama.yaml config/my_config.yaml
   ```

   **For Cloud Mode**:
   ```bash
   # Create default config
   python -m cli.main init-config config/my_config.yaml

   # Set environment variables
   export OPENAI_API_KEY="your-key"
   export ANTHROPIC_API_KEY="your-key"
   export PERPLEXITY_API_KEY="your-key"
   ```

### 6. First Research Project

Let's run your first research project!

**Step 1: Choose Your Topic**
```bash
# Examples:
# - "Quantum Computing Trends 2025"
# - "Electric Vehicle Market Analysis"
# - "Remote Work Technology"
# - "AI in Healthcare"
```

**Step 2: Run Research**
```bash
python -m cli.main research "Your Topic Here" \
  --config config/local_ollama.yaml \
  --output reports/my_first_report.md
```

**Step 3: Review Output**
```bash
# View report
cat reports/my_first_report.md

# Or open in your preferred editor
code reports/my_first_report.md
```

**What to Expect**:
- Execution time: 15-45 minutes (depending on mode)
- Console output showing progress through 6 phases
- Final report saved to specified location
- Intermediate results saved as JSON files

**Your First Report Will Include**:
- Executive Summary
- Trend Analysis
- Historical Context
- Academic Research Findings
- News & Industry Analysis
- Books & Resources
- Key Insights & Recommendations
- Reference Tables with URLs

---

(Continue with remaining sections...)
```

**Part 2: Core Concepts** (15 minutes)
- Explain multi-agent architecture
- Describe each agent's role
- Explain LLM provider strategy
- Describe workflow phases

**Part 3: Configuration** (20 minutes)
- Detailed configuration file structure
- Each configuration section explained
- Provider-specific settings
- Agent-specific settings
- Examples for common scenarios

**Part 4: Using Cardinal Biggles** (20 minutes)
- All CLI commands with examples
- Local mode detailed usage
- Cloud mode detailed usage
- Hybrid mode examples
- HIL mode workflow

**Part 5: Advanced Topics** (10 minutes)
- Creating custom agents
- Fallback configuration
- Performance tuning
- Cost optimization strategies

**Part 6: Troubleshooting** (10 minutes)
- Common error messages and solutions
- Provider-specific issues
- Performance troubleshooting
- FAQ section

**Part 7: Reference** (5 minutes)
- CLI command reference
- Configuration schema
- Environment variables
- Output format specification

---

## 🔄 Cross-Reference Updates (20 minutes)

### Phase 4: Update Documentation Cross-References

#### Task 4.1: Update README.md

**Changes**:
- Add link to User Manual in Quick Start section
- Update documentation section to reference User Manual
- Add "Documentation" section with links to all docs

```markdown
## 📚 Documentation

- **[User Manual](docs/USER_MANUAL.md)** - Complete guide for using Cardinal Biggles
- **[Local Setup Guide](docs/LOCAL_SETUP.md)** - Running without API keys
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and internals
- **[Development Guide](CLAUDE.md)** - For contributors and developers
- **[Documentation Index](docs/README.md)** - All documentation

### Quick Links
- [Installation](docs/USER_MANUAL.md#installation)
- [Quick Start](docs/USER_MANUAL.md#quick-start)
- [Configuration](docs/USER_MANUAL.md#configuration)
- [Troubleshooting](docs/USER_MANUAL.md#troubleshooting)
- [FAQ](docs/USER_MANUAL.md#faq)
```

#### Task 4.2: Update LOCAL_SETUP.md

**Changes**:
- Add reference to User Manual for general usage
- Add link to troubleshooting in User Manual
- Cross-reference configuration section

```markdown
## See Also

- [User Manual](USER_MANUAL.md) - Complete usage guide
- [Configuration Guide](USER_MANUAL.md#configuration) - Detailed config options
- [Troubleshooting](USER_MANUAL.md#troubleshooting) - General troubleshooting
- [Main README](../README.md) - Project overview
```

#### Task 4.3: Update CLAUDE.md

**Changes**:
- Add reference to User Manual for end-users
- Note that CLAUDE.md is for developers/contributors

```markdown
## Documentation Structure

**For Users**:
- [User Manual](docs/USER_MANUAL.md) - Complete guide for using Cardinal Biggles
- [Local Setup](docs/LOCAL_SETUP.md) - Running without API keys
- [README](README.md) - Project overview

**For Developers**:
- This file (CLAUDE.md) - Development guide and internals
- [Architecture](docs/ARCHITECTURE.md) - System design
- [Development Plans](dev_plans/) - Implementation plans
```

---

## ✅ Quality Assurance (20 minutes)

### Phase 5: Verify Documentation

#### Task 5.1: Documentation Review Checklist

**Accuracy Check**:
- [ ] All code examples are correct
- [ ] All file paths are accurate
- [ ] All command examples work
- [ ] Configuration examples are valid
- [ ] Links between documents work

**Completeness Check**:
- [ ] All features are documented
- [ ] All CLI commands are documented
- [ ] All configuration options are documented
- [ ] All error messages have solutions
- [ ] All use cases are covered

**Consistency Check**:
- [ ] Terminology is consistent
- [ ] Style is consistent
- [ ] Format is consistent
- [ ] Cross-references are consistent

**Usability Check**:
- [ ] Table of contents is complete
- [ ] Navigation is clear
- [ ] Examples are practical
- [ ] Troubleshooting is helpful
- [ ] FAQ answers common questions

#### Task 5.2: Test Documentation Examples

**Commands to Test**:
```bash
# Test all CLI examples from documentation
# Test all configuration examples
# Verify all file paths exist
# Check all links resolve
```

---

## 📋 Implementation Checklist

### Phase 1: File Cleanup
- [ ] Identify temporary files
- [ ] Move test files to correct locations
- [ ] Clean up old test reports
- [ ] Review and clean log files
- [ ] Verify .gitignore is complete

### Phase 2: Organization
- [ ] Create missing directories
- [ ] Add .gitkeep files
- [ ] Create documentation index
- [ ] Update .gitignore
- [ ] Verify directory structure

### Phase 3: User Manual
- [ ] Create USER_MANUAL.md structure
- [ ] Write Part 1: Getting Started
- [ ] Write Part 2: Core Concepts
- [ ] Write Part 3: Configuration
- [ ] Write Part 4: Using Cardinal Biggles
- [ ] Write Part 5: Advanced Topics
- [ ] Write Part 6: Troubleshooting
- [ ] Write Part 7: Reference
- [ ] Write Part 8: Appendices

### Phase 4: Cross-References
- [ ] Update README.md
- [ ] Update LOCAL_SETUP.md
- [ ] Update CLAUDE.md
- [ ] Create docs/README.md
- [ ] Verify all links work

### Phase 5: Quality Assurance
- [ ] Review for accuracy
- [ ] Check for completeness
- [ ] Verify consistency
- [ ] Test usability
- [ ] Test all examples

---

## 🎯 Success Criteria

### Must Have
1. ✅ All temporary files cleaned up
2. ✅ Project structure organized
3. ✅ USER_MANUAL.md created and complete
4. ✅ All documentation cross-referenced
5. ✅ Documentation index created

### Nice to Have
1. ✅ Quick reference guide
2. ✅ Troubleshooting flowcharts
3. ✅ Example use cases
4. ✅ Video walkthrough (future)
5. ✅ Interactive tutorials (future)

---

## 📊 File Organization Summary

### Before Cleanup
```
cardinal_biggles/
├── test_llm_factory.py          # Root-level test file
├── reports/
│   └── local/
│       ├── smoke_test.md
│       ├── machine_learning_*.json
│       └── history_of_timezones_*.*  # Old test files
└── docs/
    ├── LOCAL_SETUP.md
    └── ARCHITECTURE.md (assumed)
```

### After Cleanup
```
cardinal_biggles/
├── README.md                      # Main documentation
├── CLAUDE.md                      # Developer guide
├── docs/
│   ├── README.md                  # Documentation index (NEW)
│   ├── USER_MANUAL.md             # Complete user guide (NEW)
│   ├── LOCAL_SETUP.md             # Local setup guide
│   └── ARCHITECTURE.md            # System architecture
├── tests/
│   ├── test_llm_factory.py        # Moved from root
│   └── ...
├── reports/
│   ├── .gitkeep
│   └── local/
│       ├── smoke_test.md          # Kept as reference
│       └── machine_learning_*.json # Recent test files
├── logs/
│   └── .gitignore                 # Ignore log files
└── data/
    └── .gitkeep
```

---

## 🚨 Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing links | Low | Medium | Test all links before committing |
| Documentation inconsistency | Medium | Medium | Review checklist, peer review |
| Missing features in manual | Medium | High | Cross-check with codebase |
| Accidental deletion | Low | High | Git backup, careful review |
| User confusion | Medium | Medium | Clear navigation, good examples |

---

## 📝 Deliverables

1. **Cleanup**
   - Organized file structure
   - Updated .gitignore
   - Removed temporary files

2. **Documentation**
   - `docs/USER_MANUAL.md` - Complete user manual (2000+ lines)
   - `docs/README.md` - Documentation index
   - Updated cross-references in existing docs

3. **Quality Assurance**
   - Documentation review completed
   - All examples tested
   - Links verified

---

## 🔧 Implementation Order

1. **Phase 1**: File Cleanup (20 min)
   - Identify and categorize files
   - Move misplaced files
   - Clean up old test artifacts

2. **Phase 2**: Organization (30 min)
   - Create directory structure
   - Create documentation index
   - Update .gitignore

3. **Phase 3**: User Manual (90 min)
   - Create structure
   - Write content section by section
   - Add examples and references

4. **Phase 4**: Cross-References (20 min)
   - Update README.md
   - Update existing docs
   - Verify links

5. **Phase 5**: Quality Assurance (20 min)
   - Review documentation
   - Test examples
   - Final verification

**Total Time**: 2.5-3 hours

---

**End of Development Plan**

*Created: 2025-10-14*
*Plan Status: 📋 READY FOR IMPLEMENTATION*
