# Contributing to Dyson2MQTT

Thank you for your interest in contributing to Dyson2MQTT! This document provides guidelines and setup instructions for contributors.

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git
- A Dyson device (for manual testing)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/RoyalPineapple/dyson2mqtt.git
   cd dyson2mqtt
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env  # Create from template if available
   # Edit .env with your device details
   ```

## 🧪 Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with coverage
```bash
pytest tests/ --cov=dyson2mqtt --cov-report=html
```

### Run specific test categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_config.py
```

## 🔧 Code Quality

### Automatic checks (via pre-commit)
The following checks run automatically on commit:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Code style and linting
- **mypy**: Type checking
- **bandit**: Security analysis

### Manual checks
```bash
# Format code
black dyson2mqtt/ tests/

# Sort imports
isort dyson2mqtt/ tests/

# Check code style
flake8 dyson2mqtt/ tests/

# Type checking
mypy dyson2mqtt/

# Security analysis
bandit -r dyson2mqtt/
```

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 with Black formatting (88 character line length)
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions small and focused

### Testing
- Write tests for all new functionality
- Use descriptive test names that explain the scenario
- Mock external dependencies (MQTT, device connections)
- Aim for high test coverage (>80%)

### Git Workflow
1. Create a feature branch from `master`
2. Make your changes with clear, atomic commits
3. Ensure all tests pass
4. Run code quality checks
5. Submit a pull request

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(cli): add new oscillation control command`
- `fix(tests): resolve mock application issues`
- `docs(readme): update installation instructions`

## 🐛 Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces
- Device model (if relevant)

## 💡 Feature Requests

For feature requests, please:
- Describe the use case
- Explain the expected behavior
- Consider implementation complexity
- Check if it aligns with project goals

## 🔒 Security

- Never commit sensitive information (passwords, API keys)
- Report security issues privately to maintainers
- Follow secure coding practices
- Use environment variables for configuration

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions
- Update type hints when changing interfaces
- Include examples for new features

## 🤝 Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests for new functionality**
5. **Ensure all tests pass**
6. **Update documentation**
7. **Submit the pull request**

### PR Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No sensitive data is included
- [ ] Changes are focused and atomic

## 🏷️ Release Process

Releases are managed by maintainers:
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a release tag
4. Build and publish to PyPI

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Code Review**: All PRs require review before merging

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Dyson2MQTT! 🎉
