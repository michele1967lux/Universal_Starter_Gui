# Contributing to Universal Starter GUI

First off, thank you for considering contributing to Universal Starter GUI! It's people like you that make this project better for everyone.

## 🌟 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code samples, screenshots, etc.)
- **Describe the behavior you observed** and what you expected
- **Include your environment details** (OS, Python version, dependency versions)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most users
- **List any similar features** in other applications if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Follow the code style** of the project (PEP 8 for Python)
3. **Add or update tests** if applicable
4. **Update documentation** if you're adding features
5. **Ensure your commits follow a clear pattern**
6. **Write clear commit messages**

#### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat: Add support for Python 3.12 in Conda environments

- Updated environment creation to include Python 3.12 option
- Added validation for new Python version
- Updated documentation

Closes #123
```

## 🎯 Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- (Optional) Conda for testing Conda features

### Setup Steps

1. **Clone your fork**:
```bash
git clone https://github.com/YOUR_USERNAME/Universal_Starter_Gui.git
cd Universal_Starter_Gui
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements_STARTER_GUI.txt
```

4. **Create a branch for your work**:
```bash
git checkout -b feature/your-feature-name
```

## 🧪 Testing

Before submitting your pull request:

1. **Run the test suite**:
```bash
python test_starter.py
```

2. **Test manually**:
- Run the application and test your changes
- Try different scenarios
- Test on your target platform (Windows/Linux/macOS)

3. **Check for common issues**:
- No syntax errors
- No import errors
- UI elements work as expected
- No console errors or warnings

## 📝 Code Style Guidelines

### Python Code

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for classes and functions
- Keep functions small and focused
- Use meaningful variable names

Example:
```python
def create_venv(self, name: str, path: str) -> bool:
    """
    Create a new virtual environment.
    
    Args:
        name: Name of the environment
        path: Path where to create the environment
        
    Returns:
        True if successful, False otherwise
    """
    # Implementation here
    pass
```

### Documentation

- Update README.md if adding features
- Update MANUALE_STARTER_GUI.md for Italian documentation
- Add comments for complex logic
- Keep documentation in sync with code

### Git Workflow

1. **Keep your fork updated**:
```bash
git remote add upstream https://github.com/michele1967lux/Universal_Starter_Gui.git
git fetch upstream
git merge upstream/main
```

2. **Make your changes** in your feature branch

3. **Commit your changes**:
```bash
git add .
git commit -m "feat: Your descriptive commit message"
```

4. **Push to your fork**:
```bash
git push origin feature/your-feature-name
```

5. **Create a Pull Request** on GitHub

## 🌍 Translation Contributions

We welcome translations to make the application accessible to more users!

### Adding a New Language

1. **Translate UI strings** in the code
2. **Create documentation** in the target language
3. **Update README.md** with language section
4. **Test thoroughly** to ensure proper display

## 🔍 Code Review Process

After you submit a pull request:

1. **Automated checks** will run (if configured)
2. **Maintainers will review** your code
3. **Feedback may be provided** - please respond and update
4. **Once approved**, your PR will be merged!

### What We Look For

- ✅ Code quality and style
- ✅ Functionality and correctness
- ✅ Test coverage
- ✅ Documentation updates
- ✅ No breaking changes (or properly documented)
- ✅ Performance considerations

## 🤔 Questions?

- Open a **GitHub Discussion** for general questions
- Open an **Issue** for bug reports or feature requests
- Tag maintainers in PR comments if you need attention

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Trolling, insulting/derogatory comments
- Public or private harassment
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

## 🙏 Thank You!

Your contributions help make Universal Starter GUI better for everyone. We appreciate your time and effort!

---

**Happy Coding! 🚀**
