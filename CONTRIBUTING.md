# Contributing to Algo Trading System

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- Git
- VSCode (recommended)

### Local Development
1. Fork the repository
2. Clone your fork
3. Follow setup instructions in README.md
4. Create a feature branch
5. Make your changes
6. Test thoroughly
7. Submit a pull request

## Code Standards

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where possible
- Add docstrings to all functions
- Write unit tests for new features
- Use async/await for I/O operations

### JavaScript (Frontend)
- Use JSX only (no TypeScript)
- Follow React best practices
- Use functional components with hooks
- Implement proper error boundaries
- Add PropTypes for type checking

### General
- Write clear commit messages
- Keep functions small and focused
- Add comments for complex logic
- Update documentation for new features

## Adding New Features

### New Trading Strategy
1. Create strategy class in `backend/services/strategies.py`
2. Implement `generate_signals()` method
3. Add strategy to configuration
4. Update frontend strategy selector
5. Add tests and documentation

### New Data Source
1. Extend `MarketDataService` class
2. Add new data provider integration
3. Update configuration options
4. Test with various symbols
5. Document API requirements

### UI Components
1. Create reusable components
2. Follow existing design patterns
3. Use shadcn/ui components
4. Implement responsive design
5. Add proper accessibility

## Testing

### Backend Tests
\`\`\`bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_strategies.py

# Run with coverage
python -m pytest --cov=backend
\`\`\`

### Frontend Tests
\`\`\`bash
# Run component tests
npm test

# Run e2e tests
npm run test:e2e
\`\`\`

## Pull Request Process

1. Update documentation
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## Bug Reports

Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
- Screenshots if applicable

## Feature Requests

Include:
- Use case description
- Proposed solution
- Alternative solutions
- Additional context
