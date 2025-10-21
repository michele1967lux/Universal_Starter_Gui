# Universal Starter GUI - Features Overview

## 🎯 Core Functionality

### Multi-Tab Interface

The application uses a modern tabbed interface with three main sections:

#### 1. Main Tab - Script & Environment Management
- **Environment Selection**: Choose between Venv, Conda, or system Python
- **Script List**: Visual list of all managed scripts with status indicators
- **Control Buttons**: Start/Stop individual or all scripts
- **Configuration**: Auto-save/load your workspace setup

#### 2. Git Status Tab - Integrated Git Client
- **Visual Commit Graph**: Interactive tree view of repository history
- **File Status**: See staged, unstaged, and untracked files
- **Git Operations**: Commit, push, pull, fetch, merge, revert with one click
- **Branch Management**: Create, checkout, and manage branches visually
- **Stash Support**: Save and restore uncommitted changes
- **Progress Indicators**: Real-time feedback for all Git operations

#### 3. Help Tab - Built-in Documentation
- **Usage Guide**: Contextual help for all features
- **Keyboard Shortcuts**: Quick reference for power users
- **Troubleshooting**: Common issues and solutions

---

## 🎨 User Interface Elements

### Status Indicators

```
🟢 GREEN  - Process is running successfully
⚫ GRAY   - Process is stopped or not started
🔴 RED    - Process encountered an error
```

### Button Icons

```
▶  - Start/Resume
⏹  - Stop/Terminate
➕ - Add new item
🗑  - Delete/Remove
💾 - Save configuration
🔄 - Refresh/Reload
```

---

## 🔧 Technical Architecture

### Component Hierarchy

```
App (Main Window)
├── Main Tab
│   ├── Environment Frame
│   │   ├── Environment Label
│   │   └── Action Buttons
│   ├── Files Frame (Scrollable)
│   │   └── File Entries (Dynamic)
│   ├── Control Frame
│   │   └── Global Actions
│   └── Log Console
│
├── Git Status Tab
│   ├── Header Frame
│   │   ├── Branch Info
│   │   └── Refresh Controls
│   ├── Files Frame (Scrollable)
│   │   └── Checkbox + File Status
│   ├── Stage/Unstage Buttons
│   ├── Commit Graph (Canvas)
│   ├── Action Buttons
│   └── Progress Indicators
│
└── Help Tab
    └── Documentation (Scrollable)
```

### Class Structure

```
App
├── GitManager
│   └── Git command execution
├── GitOperationManager
│   └── Async operation handling
├── EnvManagerWindow
│   ├── Venv Tab
│   └── Conda Tab
├── RequirementsEditor
├── ProcessViewer
└── Helper Functions
```

---

## 🚀 Workflow Examples

### Typical Development Workflow

1. **Setup Environment**
   ```
   Open App → Manage Environments → Create Venv → Select
   ```

2. **Add Scripts**
   ```
   Main Tab → Add File → Select script.py
   ```

3. **Run & Monitor**
   ```
   Click ▶ next to script → Monitor status indicator → Check logs
   ```

4. **Git Operations**
   ```
   Git Tab → Stage files → Commit → Push
   ```

### Environment Management Workflow

1. **Create New Environment**
   ```
   Manage Environments → Venv Tab → Enter name → Create
   Wait for completion → Select → Close
   ```

2. **Install Dependencies**
   ```
   Main Tab → Install Dependencies → Select requirements.txt
   Monitor progress in log console
   ```

3. **Clone Environment**
   ```
   Manage Environments → Select environment → Clone
   Enter new name → Wait for completion
   ```

### Git Workflow

1. **Make Changes**
   ```
   Edit files in your IDE
   ```

2. **Stage & Commit**
   ```
   Git Tab → Select modified files → Stage
   Click Commit → Enter message → Confirm
   ```

3. **Push to Remote**
   ```
   Click Push → Wait for completion
   Check progress bar
   ```

4. **Create Branch**
   ```
   Right-click on commit → Create branch from...
   Enter branch name → Checkout to new branch
   ```

---

## 🔒 Security Features

### Command Execution Safety

- ✅ **No shell=True**: All subprocess calls use list arguments
- ✅ **Input Validation**: File paths and command arguments are validated
- ✅ **Safe Git Operations**: Commands are constructed programmatically
- ✅ **No Code Injection**: User input is never directly executed

### File System Safety

- ✅ **Path Validation**: All paths are checked before operations
- ✅ **Confirmation Dialogs**: Destructive operations require confirmation
- ✅ **Error Handling**: Graceful failure with user-friendly messages
- ✅ **Permission Checks**: Operations respect file system permissions

---

## 📊 Performance Characteristics

### Asynchronous Operations

All long-running operations are executed asynchronously:

- **Environment Creation**: Background thread with progress updates
- **Git Operations**: Non-blocking with cancellation support
- **Process Monitoring**: Periodic checks without UI freeze
- **Log Updates**: Queue-based thread-safe logging

### Resource Usage

- **Memory**: ~50-100 MB typical usage
- **CPU**: Minimal when idle, spikes during operations
- **Disk I/O**: Only during environment creation or Git operations
- **Network**: Only during Git push/pull operations

---

## 🎯 Advanced Features

### Process Management

**Localhost Process Viewer**:
- Lists all processes listening on localhost
- Filters application services from system processes
- Allows termination of processes
- Auto-refresh capability

**Features**:
- Port number display
- Process ID (PID)
- Process name and command line
- Safe termination with confirmation

### Environment Operations

**Venv Operations**:
- Create, Select, Rename, Clone, Delete
- Auto-detection of existing environments
- Validation of environment integrity
- **Real-time progress bars during creation**
- **Status feedback with visual indicators**

**Conda Operations**:
- Create with Python version selection
- Clone existing environments
- List all available environments
- Full environment lifecycle management
- **Dynamic progress tracking during operations**
- **Detailed console output for troubleshooting**

### Git Integration

**Commit Graph Features**:
- Multi-branch visualization
- Automatic layout algorithm
- Interactive commit selection
- Context menu actions

**File Operations**:
- Batch staging/unstaging
- Status visualization (M/A/D/??)
- Checkbox selection interface

**Advanced Git Operations** (NEW):
- **Pull**: Fetch and merge changes from remote
- **Fetch**: Download changes without auto-merge
- **Stash**: Temporarily save uncommitted changes
- **Stash Pop**: Restore previously stashed changes
- **Branch Management**: List, create, and switch branches
- **Remote Operations**: Manage remote repositories
- **Cherry-pick**: Apply specific commits to current branch
- **Revert**: Undo specific commits safely

**Comprehensive Help Documentation**:
- Complete Git workflow guide
- Operation descriptions and best practices
- Troubleshooting for common issues
- Quick reference for all Git commands

---

## 🌐 Internationalization

### Supported Languages

- **Italian**: Primary language, full UI translation
- **English**: Documentation and code comments

### UI Text Elements

Most UI elements use Italian text:
- Button labels
- Status messages
- Dialog prompts
- Error messages

Documentation is available in both languages:
- README.md (bilingual)
- MANUALE_STARTER_GUI.md (Italian)
- CONTRIBUTING.md (English)

---

## 📈 Future Enhancements

### Planned Features

- [ ] Docker container management
- [ ] Remote execution support
- [ ] Script scheduling
- [x] Enhanced Git operations (pull, fetch, stash) - **COMPLETED**
- [x] Progress bars for long operations - **COMPLETED**
- [ ] Multi-language UI support
- [ ] Theme customization
- [ ] Script templates
- [ ] Environment comparison tools

### Community Requests

Check our [GitHub Issues](https://github.com/michele1967lux/Universal_Starter_Gui/issues) for feature requests and vote on what you'd like to see next!

---

## 📚 Additional Resources

- **Main Documentation**: [README.md](../README.md)
- **Italian Manual**: [MANUALE_STARTER_GUI.md](MANUALE_STARTER_GUI.md)
- **Contributing Guide**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **GitHub Repository**: [github.com/michele1967lux/Universal_Starter_Gui](https://github.com/michele1967lux/Universal_Starter_Gui)

---

<div align="center">

**Made with ❤️ by [michele1967lux](https://github.com/michele1967lux)**

If you find this useful, please ⭐ star the repository!

</div>
