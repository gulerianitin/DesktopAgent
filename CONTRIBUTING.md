# Contributing to Desktop Agent

Thank you for your interest in contributing to Desktop Agent! This project aims to be the premier open source AI desktop assistant for Linux.

## 🎯 Project Goals

- **Linux-first**: Optimized for Ubuntu/XFCE with native Linux integration
- **Privacy-focused**: Local-first approach, user controls their data
- **Open source**: MIT licensed, community-driven development
- **Safe testing**: Docker sandboxing for system-level operations

## 🚀 Getting Started

### Development Setup

```bash
# Fork the repository on GitHub first

# Clone your fork
git clone https://github.com/YOUR_USERNAME/DesktopAgent.git
cd DesktopAgent

# Install development dependencies
./install-ubuntu.sh

# Run tests (if available)
python -m pytest tests/

# Start development
source venv/bin/activate
python main.py
```

### Development Environment

**Recommended Setup:**
- Ubuntu 20.04+ with XFCE
- Docker for safe testing
- VS Code or your preferred editor
- Python 3.8+

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings for public methods
- Keep functions focused and testable

### Testing
- Test GUI applications in Docker containers
- Use `docker exec` commands for system testing
- Verify X11 forwarding works correctly
- Test on clean Ubuntu installations

### Security
- Never commit API keys or secrets
- Use environment variables for configuration
- Validate all user inputs
- Sandbox system-level operations in Docker

## 🐛 Bug Reports

**Before reporting:**
1. Check existing issues
2. Test in clean Ubuntu environment
3. Include Desktop Agent version
4. Provide detailed reproduction steps

**Include in bug reports:**
- Ubuntu version (`lsb_release -a`)
- Desktop environment (XFCE, GNOME, etc.)
- Python version (`python3 --version`)
- Error logs from `agent.log`

## 🔄 Pull Request Process

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Create** Pull Request on GitHub

### PR Requirements
- [ ] Code follows project style guidelines
- [ ] Tests pass (when available)
- [ ] Documentation updated if needed
- [ ] No security vulnerabilities introduced

## 🎯 Areas for Contribution

### High Priority
- **Android compatibility** research and implementation
- **Additional Linux distros** support (Fedora, Arch, etc.)
- **Plugin system** for extending functionality
- **Voice commands** integration
- **Better error handling** and user feedback

### Medium Priority
- **Unit tests** and integration tests
- **Performance optimizations** for large file operations
- **Accessibility improvements** for GUI
- **Localization** (i18n) support

### Documentation
- **Video tutorials** for common use cases
- **Example guides** for different software installations
- **API documentation** for extending the agent

## 🏗️ Architecture Notes

### Core Components
- `gui/app.py`: Main Tkinter GUI application
- `agents/file_organizer.py`: File categorization logic
- `utils/guide_executor.py`: Step-by-step command execution
- `utils/claude_client.py`: Claude API integration

### Design Principles
- **Modularity**: Each component has a single responsibility
- **Safety**: All system commands are logged and sandboxed when possible
- **User Control**: Users can review and approve all actions
- **Extensibility**: Plugin architecture for adding new capabilities

## 📞 Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions and improvements

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Happy Contributing!** 🚀