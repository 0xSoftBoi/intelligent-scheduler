# Contributing to Intelligent Scheduler

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/intelligent-scheduler.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Set up the development environment (see README.md)

## Development Guidelines

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all classes and functions
- Keep functions focused and under 50 lines when possible

### Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR: `pytest`
- Aim for >80% code coverage
- Include both unit and integration tests

### Commits

- Write clear, descriptive commit messages
- Use present tense ("Add feature" not "Added feature")
- Reference issues when applicable: "Fix #123: Description"

### Pull Requests

1. Update documentation for any changed functionality
2. Add tests for new features
3. Ensure CI passes
4. Request review from maintainers
5. Address review comments promptly

## Areas for Contribution

- **Features**: Implement items from the roadmap
- **Bug Fixes**: Check open issues for bugs
- **Documentation**: Improve guides and API docs
- **Tests**: Increase test coverage
- **Performance**: Optimize algorithms
- **Integrations**: Add new calendar providers

## Code Review Process

1. Maintainers review PRs within 3-5 business days
2. Address feedback and update PR
3. Once approved, maintainer will merge

## Questions?

Open an issue with the "question" label or reach out to maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
