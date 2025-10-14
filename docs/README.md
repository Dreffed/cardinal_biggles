# Cardinal Biggles Documentation

Welcome to the Cardinal Biggles documentation! This guide will help you find the information you need.

## 📚 Documentation Overview

### For Users

#### Getting Started
- **[User Manual](USER_MANUAL.md)** - Complete guide for using Cardinal Biggles
  - Installation and setup
  - Running your first research project
  - Configuration options
  - CLI commands and usage
  - Troubleshooting and FAQ

- **[Quick Start](../README.md#-quick-start)** - Get running in 5 minutes
  - Basic installation
  - Simple usage examples

- **[Local Setup Guide](LOCAL_SETUP.md)** - Run without API keys
  - Ollama installation
  - Local model setup
  - Performance expectations
  - Troubleshooting local mode

#### Configuration

- **[Configuration Guide](USER_MANUAL.md#part-3-configuration)** - Detailed configuration options
  - LLM provider configuration
  - Agent-specific settings
  - Research parameters
  - Output customization

- **[Multi-Provider Setup](USER_MANUAL.md#cloud-mode-with-api-keys)** - Using cloud providers
  - OpenAI, Claude, Perplexity setup
  - API key management
  - Cost optimization

- **[Hybrid Mode](USER_MANUAL.md#hybrid-mode-mixed-providers)** - Mix local and cloud
  - Cost-effective configurations
  - Performance tuning

### For Developers

- **[Architecture Guide](ARCHITECTURE.md)** - System design and internals
  - Component architecture
  - Agent communication
  - Workflow patterns

- **[Development Guide](../CLAUDE.md)** - For contributors
  - Code structure
  - Adding custom agents
  - Testing patterns
  - Development workflow

- **[Development Plans](../dev_plans/)** - Implementation plans
  - Completed features
  - Future roadmap

## 🎯 Quick Navigation

### Common Tasks

| I want to... | Go to... |
|--------------|----------|
| Install Cardinal Biggles | [User Manual - Installation](USER_MANUAL.md#5-installation) |
| Run my first research | [User Manual - First Research Project](USER_MANUAL.md#6-first-research-project) |
| Use local models (no API keys) | [Local Setup Guide](LOCAL_SETUP.md) |
| Configure cloud providers | [User Manual - Cloud Mode](USER_MANUAL.md#cloud-mode-with-api-keys) |
| Understand the architecture | [Architecture Guide](ARCHITECTURE.md) |
| Add a custom agent | [Development Guide](../CLAUDE.md#adding-custom-agents) |
| Troubleshoot issues | [User Manual - Troubleshooting](USER_MANUAL.md#part-6-troubleshooting) |
| See example configurations | [User Manual - Appendices](USER_MANUAL.md#part-8-appendices) |

### By User Type

#### Researchers & Analysts
- [User Manual](USER_MANUAL.md) - Complete usage guide
- [Configuration Examples](USER_MANUAL.md#example-configurations) - Pre-configured setups
- [Best Practices](USER_MANUAL.md#best-practices) - Optimize your research

#### Developers & Contributors
- [Development Guide](../CLAUDE.md) - Code internals
- [Architecture Guide](ARCHITECTURE.md) - System design
- [Adding Features](../CLAUDE.md#development-patterns) - Extend Cardinal Biggles

#### System Administrators
- [Local Setup Guide](LOCAL_SETUP.md) - On-premise deployment
- [Performance Optimization](USER_MANUAL.md#performance-optimization) - Tuning
- [Cost Management](USER_MANUAL.md#cost-management) - Budget control

## 📖 Documentation Files

### Main Documentation

| File | Description | Audience |
|------|-------------|----------|
| [USER_MANUAL.md](USER_MANUAL.md) | Complete user guide (2000+ lines) | All users |
| [LOCAL_SETUP.md](LOCAL_SETUP.md) | Local Ollama setup (450+ lines) | Users without API keys |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture | Developers |
| [README.md](../README.md) | Project overview | Everyone |
| [CLAUDE.md](../CLAUDE.md) | Development guide | Developers |

### Additional Resources

| Resource | Location | Description |
|----------|----------|-------------|
| Example Configs | [config/](../config/) | Sample configuration files |
| Scripts | [scripts/](../scripts/) | Setup and test scripts |
| Dev Plans | [dev_plans/](../dev_plans/) | Implementation plans |
| Tests | [tests/](../tests/) | Test files and examples |

## 🔍 Search Documentation

### By Topic

#### Installation & Setup
- [Installation](USER_MANUAL.md#5-installation)
- [Quick Start](../README.md#-quick-start)
- [Local Setup](LOCAL_SETUP.md)
- [Environment Variables](USER_MANUAL.md#environment-variables)

#### Configuration
- [Configuration Overview](USER_MANUAL.md#12-configuration-overview)
- [LLM Providers](USER_MANUAL.md#13-llm-provider-configuration)
- [Agent Configuration](USER_MANUAL.md#14-agent-configuration)
- [Research Parameters](USER_MANUAL.md#15-research-parameters)

#### Usage
- [CLI Commands](USER_MANUAL.md#18-cli-commands)
- [Running Research](USER_MANUAL.md#19-running-research)
- [Local Mode](USER_MANUAL.md#20-local-mode-no-api-keys)
- [Cloud Mode](USER_MANUAL.md#21-cloud-mode-api-keys)
- [HIL Mode](USER_MANUAL.md#23-human-in-the-loop-mode)

#### Troubleshooting
- [Common Issues](USER_MANUAL.md#30-common-issues)
- [Error Messages](USER_MANUAL.md#31-error-messages)
- [FAQ](USER_MANUAL.md#34-faq)

## 🆘 Getting Help

### If you're stuck:

1. **Check the FAQ**: [User Manual FAQ](USER_MANUAL.md#34-faq)
2. **Review Troubleshooting**: [Common Issues](USER_MANUAL.md#30-common-issues)
3. **Check Examples**: [Configuration Examples](USER_MANUAL.md#40-example-configurations)
4. **Read the Manual**: [User Manual](USER_MANUAL.md)

### Still need help?

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: Suggest improvements to docs

## 📝 Documentation Standards

### For Contributors

When updating documentation:

1. **Keep it current**: Update docs when changing code
2. **Be comprehensive**: Cover all features and options
3. **Use examples**: Show, don't just tell
4. **Test examples**: Verify all code examples work
5. **Cross-reference**: Link related sections
6. **Use clear language**: Write for your audience

### Documentation Structure

```
docs/
├── README.md           # This file - Documentation index
├── USER_MANUAL.md      # Complete user guide
├── LOCAL_SETUP.md      # Local setup guide
└── ARCHITECTURE.md     # Architecture documentation
```

## 🔄 Recent Updates

### Latest Changes

- **2025-10-14**: Added comprehensive User Manual
- **2025-10-14**: Created Local Setup Guide
- **2025-10-14**: Added Human-in-the-Loop (HIL) mode
- **2025-10-14**: Created documentation index (this file)

See [CHANGELOG](USER_MANUAL.md#43-changelog) for full history.

## 📋 Documentation Checklist

When contributing documentation:

- [ ] Information is accurate and tested
- [ ] Code examples work correctly
- [ ] Links to other docs are correct
- [ ] Screenshots/diagrams are current (if applicable)
- [ ] Grammar and spelling checked
- [ ] Appropriate audience level
- [ ] Cross-references added where helpful
- [ ] Table of contents updated (if applicable)

---

**Need something?** Use the quick navigation above or check the [User Manual](USER_MANUAL.md) table of contents.

**Contributing?** See the [Development Guide](../CLAUDE.md) for code documentation standards.

**Lost?** Start with the [Quick Start](../README.md#-quick-start) guide!
