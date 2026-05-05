# Contributing to JARVIS

Thank you for your interest in contributing to JARVIS! This document provides guidelines and instructions for contributing.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

---

## 📜 Code of Conduct

This project follows a Code of Conduct. By participating, you are expected to uphold this code:

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Maintain a harassment-free environment

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- Ollama (for testing LLM features)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/jarvis.git
   cd jarvis
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/jarvis.git
   ```

---

## 💻 Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

### Frontend

```bash
cd electron-app
npm install
```

### Running in Development

**Terminal 1 (Backend):**
```bash
cd backend
python main.py
```

**Terminal 2 (Frontend):**
```bash
cd electron-app
npm run dev
```

---

## ✏️ Making Changes

### Branch Naming

Use descriptive branch names:

| Type | Format | Example |
|------|--------|---------|
| Feature | `feature/description` | `feature/voice-activation` |
| Bug Fix | `fix/description` | `fix/ocr-crash` |
| Docs | `docs/description` | `docs/api-reference` |
| Refactor | `refactor/description` | `refactor/plugin-loader` |

### Creating a Branch

```bash
git checkout -b feature/my-awesome-feature
```

### Commit Messages

Follow conventional commits:

```
type(scope): brief description

Longer description if needed.

Fixes #123
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code restructure
- `test` - Tests
- `chore` - Maintenance

**Examples:**
```
feat(plugins): add browser automation plugin
fix(ocr): handle empty screenshot gracefully
docs(readme): add troubleshooting section
```

---

## 🔀 Pull Request Process

### Before Submitting

1. ✅ Update your branch with latest upstream
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. ✅ Run tests
   ```bash
   # Backend
   cd backend && pytest
   
   # Frontend
   cd electron-app && npm test
   ```

3. ✅ Check code style
   ```bash
   # Backend
   black . && isort .
   
   # Frontend
   npm run lint
   ```

4. ✅ Update documentation if needed

### Submitting

1. Push your branch:
   ```bash
   git push origin feature/my-awesome-feature
   ```

2. Open a Pull Request on GitHub

3. Fill in the PR template:
   - Description of changes
   - Related issues
   - Testing done
   - Screenshots (if UI changes)

### Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, your PR will be merged

---

## 📐 Coding Standards

### Python (Backend)

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Max line length: 100 characters

```python
def my_function(param1: str, param2: int = 0) -> dict:
    """
    Brief description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    return {"result": param1}
```

### JavaScript/React (Frontend)

- Use ES6+ features
- Functional components with hooks
- PropTypes or TypeScript
- Meaningful variable names

```javascript
const MyComponent = ({ title, onAction }) => {
  const [state, setState] = useState(null);
  
  const handleClick = useCallback(() => {
    onAction?.(state);
  }, [state, onAction]);
  
  return (
    <div className="my-component">
      <h1>{title}</h1>
      <button onClick={handleClick}>Action</button>
    </div>
  );
};
```

### CSS

- Use CSS custom properties
- BEM-like naming
- Mobile-first approach

```css
.component {
  --component-color: var(--color-primary);
}

.component-header {
  color: var(--component-color);
}

.component-header--active {
  font-weight: bold;
}
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=modules  # With coverage
```

### Frontend Tests

```bash
cd electron-app
npm test
npm run test:coverage
```

### Writing Tests

**Python:**
```python
import pytest
from modules.llm.ollama_client import OllamaClient

def test_ollama_client_init():
    client = OllamaClient()
    assert client.host == "http://localhost:11434"

@pytest.fixture
def mock_client():
    return OllamaClient(host="http://mock:11434")
```

**JavaScript:**
```javascript
import { render, screen } from '@testing-library/react';
import CommandBar from './CommandBar';

test('renders input field', () => {
  render(<CommandBar />);
  expect(screen.getByPlaceholderText(/ask jarvis/i)).toBeInTheDocument();
});
```

---

## 📚 Documentation

### What to Document

- New features
- API endpoints
- Configuration options
- Plugin development

### Where to Document

| Content | Location |
|---------|----------|
| General usage | `README.md` |
| API reference | `backend/README.md` |
| UI components | `electron-app/README.md` |
| Plugin development | `backend/plugins/README.md` |
| Changes | `CHANGELOG.md` |

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep documentation up-to-date

---

## 🎯 Areas to Contribute

### Good First Issues

Look for issues labeled `good first issue`:
- Documentation improvements
- Bug fixes
- Test coverage
- Code comments

### Feature Ideas

- Voice activation ("Hey JARVIS")
- Browser automation plugin
- Scheduled tasks
- Multi-language support
- Custom themes

---

## ❓ Questions?

- Open an issue for bugs or features
- Start a discussion for questions
- Check existing issues/discussions first

---

## 🙏 Thank You!

Your contributions make JARVIS better for everyone. Thank you for being part of the community!
