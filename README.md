# Universal Starter GUI

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
[![GitHub Stars](https://img.shields.io/github/stars/michele1967lux/Universal_Starter_Gui?style=social)](https://github.com/michele1967lux/Universal_Starter_Gui/stargazers)

**[English](#english) | [Italiano](#italiano)**

*A modern, professional desktop application for managing and launching Python scripts with integrated Git support and virtual environment management*

**⭐ If you find this project useful, please consider giving it a star! It helps the project grow and motivates continued development. ⭐**

</div>

---

## English

### ✨ Key Features

#### Script Management
- 🚀 **Launch and manage multiple scripts** with visual status indicators
- 📊 **Real-time process monitoring** with colored status indicators (running, stopped, error)
- 💻 **Localhost process viewer** to manage running services
- ⚡ **External terminal support** for interactive scripts

#### Environment Management
- 🐍 **Create, clone, rename, and delete** Python virtual environments (Venv and Conda)
- 🔄 **Easy environment switching** between projects
- 📦 **Dependency management** with built-in requirements.txt editor
- 🔍 **Library verification** and CUDA/PyTorch testing tools

#### Git Integration
- 📈 **Visual commit graph** with interactive branch visualization
- 🎯 **Stage/unstage files** with checkbox selection
- 🔀 **Merge, cherry-pick, and revert** operations
- 🌿 **Branch creation and checkout** from any commit
- ⚙️ **Asynchronous operations** with progress indicators
- 📥 **Pull and Fetch** - sync with remote repositories
- 💾 **Stash support** - temporarily save uncommitted changes
- 📖 **Comprehensive help** - complete Git guide in Help tab

#### User Experience
- 🎨 **Modern dark-themed GUI** using CustomTkinter
- 💾 **Auto-save/load configurations** for session persistence
- 📝 **Contextual tooltips** and help documentation
- 🌍 **Bilingual support** (Italian and English)

### 📋 Requirements

- **Python**: 3.9 or higher
- **Dependencies**: 
  - `customtkinter >= 5.2.0`
  - `psutil` (for process management)
- **Optional**: 
  - Conda/Miniconda/Anaconda (for Conda environment support)
  - Git (for Git integration features)

### 🔧 Installation

1. **Clone the repository**:
```bash
git clone https://github.com/michele1967lux/Universal_Starter_Gui.git
cd Universal_Starter_Gui
```

2. **Install dependencies**:
```bash
pip install -r requirements_STARTER_GUI.txt
```

3. **(Optional) Install Conda** for Conda environment support

### 🚀 Quick Start

**Windows**:
```bash
run_STARTER_GUI.bat
```

**Linux/macOS**:
```bash
chmod +x run_STARTER_GUI.sh
./run_STARTER_GUI.sh
```

Or run directly:
```bash
python universal_STARTER_GUI.py
```

### 📖 Usage Guide

#### 1. Environment Management
- Click **"Gestisci Ambienti"** (Manage Environments) to open the environment manager
- Choose between **Venv** or **Conda** tabs
- Create new environments or select existing ones
- Clone or rename environments as needed

#### 2. Script Management
- Click **"➕ Aggiungi File"** to add Python scripts
- Use **▶** to start individual scripts
- Use **⏹** to stop running scripts  
- Check **"Lancia in nuova shell"** to run scripts in external terminals

#### 3. Git Operations
- Switch to **"Git Status"** tab for Git features
- View commit history in the visual graph
- Click commits to checkout, create branches, or cherry-pick
- Stage/unstage files using checkboxes
- Use buttons for common operations:
  - **Commit**: Save staged changes
  - **Push**: Upload commits to remote
  - **Pull**: Download and merge remote changes
  - **Fetch**: Download remote changes without merging
  - **Stash**: Temporarily save uncommitted work
  - **Merge**: Combine branches
- Access comprehensive Git help in the Help tab

#### 4. Dependency Management
- Click **"Installa Dipendenze"** to install from requirements.txt
- Use **"Editor Requirements"** to create/edit requirements
- Click **"Verifica Librerie"** to list installed packages

#### 5. Process Management
- Click **"Processi Localhost"** to view running services
- Filter by application services
- Terminate processes directly from the viewer

### 📊 Status Indicators

| Indicator | Meaning |
|-----------|---------|
| 🟢 Green  | Process running successfully |
| ⚫ Gray   | Process stopped or not started |
| 🔴 Red    | Process error or crashed |

### 📁 Project Structure

```
Universal_Starter_Gui/
├── universal_STARTER_GUI.py      # Main application
├── test_starter.py                # Test suite
├── requirements_STARTER_GUI.txt   # Python dependencies
├── config_STARTER_GUI.json        # Configuration file (auto-generated)
├── MANUALE_STARTER_GUI.md         # Italian user manual
├── README.md                      # This file (bilingual)
├── run_STARTER_GUI.bat            # Windows launcher
├── run_STARTER_GUI.sh             # Unix launcher
├── examples/                      # Example scripts
│   ├── example_simple.py
│   ├── example_server.py
│   └── example_worker.py
└── .venvs/                        # Virtual environments (auto-created)
```

### 🧪 Testing

Run the test suite:
```bash
python test_starter.py
```

The test suite validates:
- Git integration features
- Configuration management
- Environment operations

### 🎯 Advanced Features

#### Git Integration Details
The integrated Git client provides:
- **Visual Commit Graph**: Interactive tree view of commit history with multiple branch support
- **Smart Layout Algorithm**: Automatically positions commits in columns for clear branch visualization
- **Asynchronous Operations**: All Git operations run in background threads to prevent UI freezing
- **Context Menus**: Right-click commits for quick actions (checkout, branch creation, cherry-pick)
- **Progress Tracking**: Visual feedback for long-running operations with cancellation support
- **Complete Operations**: Pull, fetch, push, merge, stash, revert, cherry-pick, and more
- **Comprehensive Help**: Built-in documentation covers all Git workflows and troubleshooting

#### Environment Management Details
- **Venv Operations**: Create, clone, rename, and delete Python venv environments
- **Conda Operations**: Full support for Conda environment lifecycle
- **Auto-detection**: Automatically finds existing environments in standard locations
- **Validation**: Checks environment integrity before selection
- **Console Output**: Real-time feedback during environment operations
- **Progress Bars**: Visual indicators show creation progress with status labels
- **Error Handling**: Clear feedback for operation failures with troubleshooting hints

#### Process Management
- **Service Detection**: Automatically identifies application services vs system processes
- **Port Monitoring**: Lists all processes listening on localhost ports
- **Safe Termination**: Graceful process shutdown with confirmation dialogs
- **Real-time Updates**: Refresh process list on demand

### 🔒 Code Quality & Security

This project follows professional development practices:
- ✅ Modular architecture with clear separation of concerns
- ✅ Type hints for better code clarity
- ✅ Error handling with user-friendly messages
- ✅ Thread-safe operations for concurrent tasks
- ✅ Input validation to prevent command injection
- ✅ Clean Git implementation without shell=True vulnerabilities

### 🛠️ Development

#### Code Architecture

The application follows a clean, modular design:

**Core Classes**:
- `App`: Main application window with tabbed interface
- `GitManager`: Handles all Git operations with clean command execution
- `GitOperationManager`: Manages asynchronous Git operations
- `EnvManagerWindow`: Environment creation and management UI
- `RequirementsEditor`: Requirements.txt editor window
- `ProcessViewer`: Localhost process management window

**Key Design Patterns**:
- **Separation of Concerns**: Git logic separated from UI code
- **Observer Pattern**: Queue-based communication between threads and UI
- **Async Operations**: Background threads for long-running tasks
- **Factory Pattern**: Command building based on environment type

#### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### 🐛 Known Issues & Limitations

- Script console output is not displayed in GUI by design (use external shell option if needed)
- Conda operations require Conda to be in system PATH
- Git operations require Git to be installed and accessible
- Administrator privileges may be required on Windows for some operations
- Process termination for external shell scripts is limited

### 💡 FAQ

**Q: Can I use the app without Conda?**  
A: Yes! Venv support is fully functional. Conda is entirely optional.

**Q: Where are Venv environments stored?**  
A: In the `.venvs` directory within the application folder.

**Q: Does it work with Docker?**  
A: No, Docker is not currently supported. Only Python Venv and Conda environments.

**Q: Can I add non-Python scripts?**  
A: Yes! Any executable file can be added and launched.

**Q: How do I see script output?**  
A: Check the "Lancia in nuova shell" option to run scripts in external terminals, or check the Log Output section.

### 🤝 Contributing

We welcome contributions! Here's how you can help:

- ⭐ **Star this repository** if you find it useful
- 🐛 **Report bugs** by opening an issue
- 💡 **Suggest features** through discussions
- 🔧 **Submit pull requests** with improvements
- 📖 **Improve documentation** in any language
- 🌍 **Add translations** for more languages

### 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

This means you can:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

### 👥 Authors & Acknowledgments

**Main Developer**: [michele1967lux](https://github.com/michele1967lux)

**Built With**:
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern UI framework
- [psutil](https://github.com/giampaolo/psutil) - Process and system utilities
- Python standard library

**Special Thanks**:
- The CustomTkinter community for an excellent UI framework
- All contributors and users who provide feedback

### 🌟 Support the Project

If this project has been helpful to you, please consider:
- ⭐ **Starring the repository** on GitHub
- 🐦 **Sharing it** on social media
- 💬 **Writing about your experience** using it
- 🤝 **Contributing** code or documentation

**Your support helps maintain and improve this project!**

---

## Italiano

### 📖 Panoramica

**Universal Starter GUI** è un'applicazione desktop moderna e professionale per gestire e lanciare script Python con supporto integrato per Git e gestione di ambienti virtuali. Progettata per sviluppatori che lavorano su più progetti contemporaneamente.

### ✨ Caratteristiche Principali

#### Gestione Script
- 🚀 **Avvia e gestisci più script** con indicatori di stato visivi
- 📊 **Monitoraggio processi in tempo reale** con indicatori colorati
- 💻 **Visualizzatore processi localhost** per gestire servizi in esecuzione
- ⚡ **Supporto terminale esterno** per script interattivi

#### Gestione Ambienti
- 🐍 **Crea, clona, rinomina ed elimina** ambienti virtuali Python (Venv e Conda)
- 🔄 **Cambio ambiente facile** tra progetti diversi
- 📦 **Gestione dipendenze** con editor requirements.txt integrato
- 🔍 **Verifica librerie** e strumenti di test CUDA/PyTorch

#### Integrazione Git
- 📈 **Grafico commit visuale** con visualizzazione interattiva dei branch
- 🎯 **Stage/unstage file** con selezione tramite checkbox
- 🔀 **Operazioni merge, cherry-pick e revert**
- 🌿 **Creazione branch e checkout** da qualsiasi commit
- ⚙️ **Operazioni asincrone** con indicatori di progresso
- 📥 **Pull e Fetch** - sincronizza con repository remoti
- 💾 **Supporto Stash** - salva temporaneamente modifiche non committed
- 📖 **Guida completa** - documentazione Git completa nella sezione Help

### 📋 Requisiti

- **Python**: 3.9 o superiore
- **Dipendenze**: `customtkinter >= 5.2.0`, `psutil`
- **Opzionali**: Conda/Miniconda/Anaconda, Git

### 🔧 Installazione

1. **Clona il repository**:
```bash
git clone https://github.com/michele1967lux/Universal_Starter_Gui.git
cd Universal_Starter_Gui
```

2. **Installa le dipendenze**:
```bash
pip install -r requirements_STARTER_GUI.txt
```

### �� Avvio Rapido

**Windows**: `run_STARTER_GUI.bat`  
**Linux/macOS**: `./run_STARTER_GUI.sh`  
**Diretto**: `python universal_STARTER_GUI.py`

### 📖 Guida all'Uso

#### Gestione Ambienti
Clicca **"Gestisci Ambienti"** → Seleziona Venv o Conda → Crea/Seleziona ambiente

#### Gestione Script  
**"➕ Aggiungi File"** → Seleziona script → **▶** per avviare → **⏹** per fermare

#### Operazioni Git
Tab **"Git Status"** → Visualizza commit → Click per azioni → Stage/Commit/Push

#### Gestione Dipendenze
**"Installa Dipendenze"** / **"Editor Requirements"** / **"Verifica Librerie"**

### 📊 Indicatori di Stato

| Indicatore | Significato |
|-----------|-------------|
| 🟢 Verde  | Processo in esecuzione |
| ⚫ Grigio  | Processo fermato |
| 🔴 Rosso   | Errore processo |

### 🔒 Qualità del Codice

✅ Architettura modulare  
✅ Type hints e documentazione  
✅ Gestione errori robusta  
✅ Operazioni thread-safe  
✅ Validazione input sicura  
✅ Implementazione Git pulita

### 💡 FAQ

**Q: Funziona senza Conda?** → Sì, Venv è completamente supportato  
**Q: Dove sono gli ambienti?** → Directory `.venvs`  
**Q: Supporta Docker?** → No, solo Venv e Conda  
**Q: Posso usare altri linguaggi?** → Sì, qualsiasi eseguibile

### 🤝 Contribuisci

⭐ **Metti una stella** se ti è utile!  
🐛 Segnala bug | 💡 Suggerisci funzionalità | 🔧 Invia PR | 📖 Migliora docs

### 📄 Licenza

**MIT License** - Uso libero, commerciale, modifica, distribuzione

### 👥 Autori

**Sviluppatore**: [michele1967lux](https://github.com/michele1967lux)

**Tecnologie**: CustomTkinter, psutil, Python stdlib

### 🌟 Supporta il Progetto

- ⭐ **Stella su GitHub**
- 🐦 **Condividi sui social**
- 💬 **Scrivi della tua esperienza**
- 🤝 **Contribuisci al codice**

---

<div align="center">

**📚 Documentazione completa: [MANUALE_STARTER_GUI.md](docs/MANUALE_STARTER_GUI.md)**

**Made with ❤️ by [michele1967lux](https://github.com/michele1967lux)**

[![Stars](https://img.shields.io/github/stars/michele1967lux/Universal_Starter_Gui?style=social)](https://github.com/michele1967lux/Universal_Starter_Gui/stargazers)

**Version 1.3** | October 2025

### 🆕 What's New in v1.3
- ✨ **Enhanced Git Operations**: Pull, Fetch, Stash/Stash Pop support
- 📊 **Progress Bars**: Real-time feedback for environment creation
- 📖 **Comprehensive Git Guide**: Complete help documentation in the Help tab
- 🧪 **Improved Testing**: 9 passing tests for Git and environment operations
- 🎨 **Better UX**: Visual progress indicators and status labels

</div>
