# Universal Starter GUI

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modern desktop application for managing and launching Python scripts with virtual environment support (Venv and Conda).

## ✨ Features

- 🚀 **Launch and manage multiple scripts** with visual status indicators
- 🐍 **Create and manage Python virtual environments** (both Venv and Conda)
- 💾 **Save and load configurations** automatically
- 🎨 **Modern dark-themed GUI** using CustomTkinter
- 📊 **Real-time process monitoring** with colored indicators
- ⚡ **Asynchronous environment creation** with live console output
- 🔄 **Environment switching** for different projects

## 📋 Requirements

- Python 3.9 or higher
- customtkinter >= 5.2.0
- (Optional) Conda/Miniconda/Anaconda for Conda environment support

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/mk4-67/UNIVERSAL-STARTER-GUI.git
cd UNIVERSAL-STARTER-GUI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install Conda for Conda environment support

## 🚀 Usage

Run the application:
```bash
python universal_starter.py
```

### Quick Start

1. **Select an Environment** (optional):
   - Click "Gestisci Ambienti" (Manage Environments)
   - Create a new Venv or Conda environment
   - Select the environment you want to use

2. **Add Scripts**:
   - Click "➕ Aggiungi File" to add Python scripts or executables
   - Scripts will be listed with status indicators

3. **Launch Scripts**:
   - Click ▶ next to a script to launch it individually
   - Or use "▶ Avvia Tutti" to launch all scripts

4. **Monitor Status**:
   - 🟢 Green: Running
   - ⚫ Gray: Stopped
   - 🔴 Red: Error

5. **Save Configuration**:
   - Your configuration is automatically saved to `config.json`
   - It will be restored when you restart the application

## 📖 Documentation

For detailed documentation in Italian, see [MANUALE.md](MANUALE.md).

For the original task specification, see [TASK.MD](TASK.MD).

## 🧪 Testing

Run the test suite:
```bash
python test_starter.py
```

The test suite includes:
- Configuration save/load tests
- Venv creation and listing tests
- Conda detection tests
- Script execution tests
- Command building tests

## 📁 Project Structure

```
UNIVERSAL-STARTER-GUI/
├── universal_starter.py    # Main application
├── test_starter.py          # Test suite
├── requirements.txt         # Python dependencies
├── MANUALE.md              # User manual (Italian)
├── TASK.MD                 # Original task specification
├── README.md               # This file
├── .gitignore              # Git ignore rules
└── .venvs/                 # Venv environments directory (created at runtime)
```

## 🎯 Features in Detail

### Environment Management

- **Venv Support**: Create, list, select, and delete Python venv environments
- **Conda Support**: Create, list, select, and delete Conda environments
- **Environment Switching**: Easily switch between different environments
- **Real-time Feedback**: Console output during environment creation/deletion

### Script Management

- **Multi-script Support**: Manage multiple scripts simultaneously
- **Status Monitoring**: Visual indicators for each script's status
- **Bulk Operations**: Start/stop all scripts with one click
- **Environment-aware Execution**: Scripts run in the selected environment

### Configuration

- **Auto-save**: Configuration automatically saved on changes
- **Auto-load**: Previous configuration restored on startup
- **JSON Format**: Human-readable configuration format

```json
{
  "environment": {
    "type": "venv",
    "name": "my_env",
    "path": "/path/to/.venvs/my_env"
  },
  "files": [
    {
      "name": "script.py",
      "path": "/path/to/script.py"
    }
  ]
}
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
python test_starter.py

# Run with verbose output
python -m pytest test_starter.py -v
```

### Code Structure

The application follows a modular design:

- **App**: Main application class
  - GUI setup and management
  - Configuration handling
  - Process management

- **EnvManagerWindow**: Environment management window
  - Venv tab with creation/deletion
  - Conda tab with creation/deletion
  - Real-time console output

## 🐛 Known Issues

- Console output from running scripts is not displayed in the GUI (by design)
- Windows users may need to run with administrator privileges for some operations
- Conda operations require Conda to be in the system PATH

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**mk4-67**

- GitHub: [@mk4-67](https://github.com/mk4-67)

## 🙏 Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Inspired by the need for a simple, universal script launcher

## 📸 Screenshots

### Main Window
The main window shows the active environment, file list with status indicators, and control buttons.

### Environment Manager
The environment manager allows creating, selecting, and deleting both Venv and Conda environments with real-time console feedback.

---

**Version**: 1.0  
**Date**: 2025-10-18
