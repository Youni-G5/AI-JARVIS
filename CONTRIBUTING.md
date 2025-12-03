# Contributing to AI-JARVIS

Thank you for your interest in contributing to AI-JARVIS! 🚀

## Code of Conduct

Be respectful, inclusive, and professional.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** first
2. **Use the bug template** when creating new issues
3. **Include**:
   - OS and version
   - Docker version
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs/screenshots

### Suggesting Features

1. **Check roadmap** in ROADMAP.md
2. **Open a discussion** before creating PR
3. **Describe**:
   - Use case
   - Proposed solution
   - Alternatives considered

### Pull Requests

#### Before Starting

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Discuss major changes** in an issue first

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/AI-JARVIS.git
cd AI-JARVIS

# Install dependencies
make install

# Start development environment
make dev
```

#### Code Standards

**Python**:
- Follow PEP 8
- Use type hints
- Add docstrings
- Run linters:
  ```bash
  make lint
  make format
  ```

**JavaScript/TypeScript**:
- Follow project ESLint rules
- Use TypeScript types
- Format with Prettier

#### Testing

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Test specific component
pytest apps/orchestrator_core/tests/ -v
```

**Requirements**:
- Add tests for new features
- Maintain 80%+ coverage
- All tests must pass

#### Commit Messages

Follow conventional commits:

```
feat: add voice activation feature
fix: resolve memory leak in orchestrator
docs: update installation guide
test: add vision service tests
refactor: improve action executor performance
```

#### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Run all tests**: `make test`
4. **Run linters**: `make lint`
5. **Update CHANGELOG.md**
6. **Create PR** with clear description
7. **Link related issues**
8. **Wait for review**

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Added comments for complex logic
- [ ] Updated documentation
- [ ] Added/updated tests
- [ ] All tests pass
- [ ] No new warnings
- [ ] Updated CHANGELOG.md

## Project Structure

```
AI-JARVIS/
├── apps/                 # Microservices
│   ├── orchestrator_core/ # Main orchestrator
│   ├── stt_service/       # Speech-to-text
│   ├── tts_service/       # Text-to-speech
│   ├── llm_agent/         # LLM wrapper
│   ├── vision_service/    # Computer vision
│   └── action_executor/   # Action execution
│
├── frontend/            # Next.js dashboard
├── docs/                # Documentation
├── prompts/             # LLM prompts
├── tests/               # Integration tests
└── infra/               # Infrastructure configs
```

## Getting Help

- 💬 **Discussions**: Ask questions
- 🐛 **Issues**: Report bugs
- 📧 **Email**: For security issues

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

---

**Thank you for contributing!** 🙏