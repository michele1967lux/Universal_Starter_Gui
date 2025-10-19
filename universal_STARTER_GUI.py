#!/usr/bin/env python3
"""
Universal Starter GUI - A modern desktop application for managing and launching scripts
with Python virtual environment support (Venv and Conda).
"""

import customtkinter as ctk
import tkinter as tk
# Check CustomTkinter version
try:
    import importlib.metadata
    ctk_version = importlib.metadata.version("customtkinter")
    if tuple(map(int, ctk_version.split('.'))) < (5, 2, 0):
        raise ImportError(f"CustomTkinter version {ctk_version} is too old. Requires >= 5.2.0")
except ImportError as e:
    print(f"Error with CustomTkinter: {e}")
    sys.exit(1)

import subprocess
import threading
import queue
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import shutil
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import psutil


def run_install_command(command: List[str], q: queue.Queue):
    """Run the install command and put output into queue."""
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in process.stdout:
            q.put(line.strip())

        process.wait()

        if process.returncode == 0:
            q.put("[SUCCESS] Installazione dipendenze completata!")
        else:
            q.put(f"[ERROR] Installazione fallita (codice: {process.returncode})")
    except Exception as e:
        q.put(f"[ERROR] {str(e)}")
    finally:
        q.put(None)


def read_process_output(process: subprocess.Popen, q: queue.Queue, name: str):
    """Read stdout and stderr from a process and put into queue."""
    try:
        # Read stdout
        for line in process.stdout:
            log_queue.put(f"[{name}] {line}")
        # Read stderr
        for line in process.stderr:
            log_queue.put(f"[{name} ERR] {line}")
    except Exception as e:
        log_queue.put(f"[{name}] Errore lettura output: {e}\n")
    finally:
        q.put(None)  # Signal completion


def monitor_install_queue(q: queue.Queue, app):
    """Monitor the install output queue."""
    try:
        while True:
            line = q.get_nowait()
            if line is None:
                break
            log_queue.put(line)
    except queue.Empty:
        app.after(100, lambda: monitor_install_queue(q, app))

# Global log queue for thread-safe logging to GUI
log_queue = queue.Queue()


def log_to_console(console: ctk.CTkTextbox, message: str):
    """Log a message to a console textbox."""
    try:
        console.configure(state="normal")
        console.insert("end", message)
        console.see("end")
        console.configure(state="disabled")
    except Exception as e:
        print(f"Error logging to console: {e}")


class RequirementsEditor(ctk.CTkToplevel):
    """Window for editing requirements.txt."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Editor Requirements")
        self.geometry("600x500")

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # Textbox for editing
        self.textbox = ctk.CTkTextbox(self, wrap="word")
        self.textbox.pack(pady=10, padx=10, fill="both", expand=True)

        # Buttons frame
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=5, padx=10, fill="x")

        load_btn = ctk.CTkButton(btn_frame, text="Carica", command=self.load_file)
        load_btn.pack(side="left", padx=5)

        save_btn = ctk.CTkButton(btn_frame, text="Salva", command=self.save_file)
        save_btn.pack(side="left", padx=5)

        install_btn = ctk.CTkButton(btn_frame, text="Installa", command=self.install_requirements, fg_color="green")
        install_btn.pack(side="left", padx=5)

        close_btn = ctk.CTkButton(btn_frame, text="Chiudi", command=self.destroy)
        close_btn.pack(side="right", padx=5)

    def load_file(self):
        """Load requirements from file."""
        file_path = ctk.filedialog.askopenfilename(
            title="Seleziona requirements.txt",
            filetypes=[("Requirements", "requirements.txt"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.textbox.delete("1.0", "end")
                self.textbox.insert("1.0", content)
            except Exception as e:
                messagebox.showerror("Errore", f"Errore caricamento file: {e}")

    def save_file(self):
        """Save requirements to file."""
        file_path = ctk.filedialog.asksaveasfilename(
            title="Salva requirements.txt",
            defaultextension=".txt",
            filetypes=[("Requirements", "requirements.txt"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                content = self.textbox.get("1.0", "end").strip()
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Successo", "File salvato con successo!")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore salvataggio file: {e}")

    def install_requirements(self):
        """Install the requirements in the active environment."""
        if not self.parent.env_type:
            messagebox.showerror("Errore", "Selezionare un ambiente prima di installare.")
            return

        content = self.textbox.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Attenzione", "Nessuna dipendenza da installare.")
            return

        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_file = f.name

        # Install using existing method
        self.parent.install_dependencies(temp_file)

        # Clean up temp file
        os.unlink(temp_file)


def get_localhost_processes(filter_type="all"):
    """Get list of processes listening on localhost."""
    processes = []
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN' and conn.laddr:
                # Accept both 127.0.0.1 and 0.0.0.0 bindings
                if conn.laddr.ip in ['127.0.0.1', '0.0.0.0']:
                    try:
                        proc = psutil.Process(conn.pid)
                        process_info = {
                            'port': conn.laddr.port,
                            'pid': conn.pid,
                            'name': proc.name(),
                            'cmdline': ' '.join(proc.cmdline())[:100] if proc.cmdline() else ''
                        }

                        # Apply filter
                        if filter_type == "app_services":
                            if not is_app_service(process_info):
                                continue

                        processes.append(process_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
    except Exception as e:
        print(f"Error getting processes: {e}")
    return sorted(processes, key=lambda x: x['port'])


def is_app_service(proc):
    """Determine if a process is an application service (not system service)."""
    name = proc['name'].lower()
    cmdline = proc['cmdline'].lower()
    port = proc['port']

    # Exclude known system services
    system_services = ['nahimic', 'norton', 'antivirus', 'defender', 'windows',
                      'svchost', 'system', 'idle', 'csrss', 'smss', 'lsass']
    if any(s in name for s in system_services):
        return False

    # Include development servers
    dev_servers = ['uvicorn', 'fastapi', 'flask', 'django', 'gunicorn',
                  'node', 'npm', 'yarn', 'express', 'next', 'react']
    if any(s in cmdline for s in dev_servers):
        return True

    # Include common development ports
    if 3000 <= port <= 9999:
        return True

    # Include Python/Node processes with server/app indicators
    if ('python' in name or 'node' in name or 'ollama' in name or 'studio' in name) and \
       ('server' in cmdline or 'app' in cmdline or 'api' in cmdline or 'main' in cmdline):
        return True

    # Include databases if they seem user-started (not system)
    if port in [3306, 5432, 27017, 6379] and 'service' not in cmdline:
        return True

    return False


class ProcessViewer(ctk.CTkToplevel):
    """Window for viewing and managing localhost processes."""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Processi Localhost")
        self.geometry("800x600")

        # Make window modal
        self.transient(parent)
        self.grab_set()

        # Filter controls
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(pady=5, padx=10, fill="x")

        self.show_app_only = ctk.BooleanVar(value=True)
        app_filter_cb = ctk.CTkCheckBox(filter_frame, text="Mostra solo servizi app",
                                       variable=self.show_app_only,
                                       command=self.load_processes)
        app_filter_cb.pack(side="left", padx=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(filter_frame, text="Aggiorna", command=self.load_processes)
        refresh_btn.pack(side="right", padx=5)

        # Scrollable frame for process list
        self.process_frame = ctk.CTkScrollableFrame(self)
        self.process_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.load_processes()

    def load_processes(self):
        """Load and display localhost processes in table format."""
        # Clear existing widgets
        for widget in self.process_frame.winfo_children():
            widget.destroy()

        # Configure grid
        self.process_frame.grid_columnconfigure(3, weight=1)  # Command column expands

        # Get processes
        filter_type = "app_services" if self.show_app_only.get() else "all"
        processes = get_localhost_processes(filter_type)

        if not processes:
            label = ctk.CTkLabel(self.process_frame, text="Nessun processo localhost trovato")
            label.grid(row=0, column=0, columnspan=5, pady=20)
            return

        # Headers
        headers = ["Porta", "PID", "Nome", "Comando", "Azione"]
        for col, header in enumerate(headers):
            hdr_label = ctk.CTkLabel(self.process_frame, text=header, font=("Arial", 12, "bold"))
            hdr_label.grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Data rows
        for row, proc in enumerate(processes, start=1):
            # Port
            port_label = ctk.CTkLabel(self.process_frame, text=str(proc['port']))
            port_label.grid(row=row, column=0, padx=5, pady=2, sticky="w")

            # PID
            pid_label = ctk.CTkLabel(self.process_frame, text=str(proc['pid']))
            pid_label.grid(row=row, column=1, padx=5, pady=2, sticky="w")

            # Name
            name_label = ctk.CTkLabel(self.process_frame, text=proc['name'])
            name_label.grid(row=row, column=2, padx=5, pady=2, sticky="w")

            # Command (truncated)
            cmd_text = proc['cmdline'][:50] + "..." if len(proc['cmdline']) > 50 else proc['cmdline']
            cmd_label = ctk.CTkLabel(self.process_frame, text=cmd_text)
            cmd_label.grid(row=row, column=3, padx=5, pady=2, sticky="w")

            # Kill button
            kill_btn = ctk.CTkButton(self.process_frame, text="Termina", fg_color="red", width=80,
                                   command=lambda p=proc: self.kill_process(p))
            kill_btn.grid(row=row, column=4, padx=5, pady=2)

    def kill_process(self, proc):
        """Kill a process with confirmation."""
        if not messagebox.askyesno("Conferma Terminazione",
                                 f"Terminare il processo '{proc['name']}' (PID: {proc['pid']})?"):
            return

        try:
            psutil.Process(proc['pid']).terminate()
            messagebox.showinfo("Successo", f"Processo {proc['pid']} terminato")
            self.load_processes()  # Refresh list
        except psutil.AccessDenied:
            messagebox.showerror("Errore", "Accesso negato. Eseguire come amministratore.")
        except psutil.NoSuchProcess:
            messagebox.showinfo("Info", "Processo già terminato")
            self.load_processes()
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile terminare processo: {e}")


class EnvManagerWindow(ctk.CTkToplevel):
    """Window for managing Python virtual environments (Venv and Conda)."""
    
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.parent = parent
        self.callback = callback
        self.title("Gestione Ambienti")
        self.geometry("800x600")
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Create tabview for Venv and Conda
        self.tabview = ctk.CTkTabview(self, width=780, height=580)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Add tabs
        self.tabview.add("Venv")
        self.tabview.add("Conda")
        
        # Setup Venv tab
        self.setup_venv_tab()
        
        # Setup Conda tab
        self.setup_conda_tab()
        
        # Refresh environment lists
        self.refresh_venv_list()
        self.refresh_conda_list()
    
    def setup_venv_tab(self):
        """Setup the Venv management tab."""
        tab = self.tabview.tab("Venv")
        
        # Existing environments section
        env_frame = ctk.CTkFrame(tab)
        env_frame.pack(pady=(10, 5), padx=10, fill="x")

        env_label = ctk.CTkLabel(env_frame, text="Ambienti Venv Esistenti:", font=("Arial", 14, "bold"))
        env_label.pack(side="left", anchor="w")

        refresh_btn = ctk.CTkButton(env_frame, text="Aggiorna", width=80, command=self.refresh_venv_list)
        refresh_btn.pack(side="right", padx=5)

        # Scrollable frame for environment list
        self.venv_list_frame = ctk.CTkScrollableFrame(tab, height=200)
        self.venv_list_frame.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Create new environment section
        create_label = ctk.CTkLabel(tab, text="Crea Nuovo Ambiente Venv:", font=("Arial", 14, "bold"))
        create_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Input frame
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(input_frame, text="Nome:").pack(side="left", padx=5)
        self.venv_name_entry = ctk.CTkEntry(input_frame, width=300)
        self.venv_name_entry.pack(side="left", padx=5)
        
        create_btn = ctk.CTkButton(input_frame, text="Crea", command=self.create_venv)
        create_btn.pack(side="left", padx=5)
        
        # Output console
        console_label = ctk.CTkLabel(tab, text="Console Output:", font=("Arial", 12, "bold"))
        console_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.venv_console = ctk.CTkTextbox(tab, height=100, state="disabled")
        self.venv_console.pack(pady=5, padx=10, fill="both")
    
    def setup_conda_tab(self):
        """Setup the Conda management tab."""
        tab = self.tabview.tab("Conda")
        
        # Existing environments section
        env_frame = ctk.CTkFrame(tab)
        env_frame.pack(pady=(10, 5), padx=10, fill="x")

        env_label = ctk.CTkLabel(env_frame, text="Ambienti Conda Esistenti:", font=("Arial", 14, "bold"))
        env_label.pack(side="left", anchor="w")

        refresh_btn = ctk.CTkButton(env_frame, text="Aggiorna", width=80, command=self.refresh_conda_list)
        refresh_btn.pack(side="right", padx=5)

        # Scrollable frame for environment list
        self.conda_list_frame = ctk.CTkScrollableFrame(tab, height=200)
        self.conda_list_frame.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Create new environment section
        create_label = ctk.CTkLabel(tab, text="Crea Nuovo Ambiente Conda:", font=("Arial", 14, "bold"))
        create_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Input frame
        input_frame = ctk.CTkFrame(tab)
        input_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(input_frame, text="Nome:").pack(side="left", padx=5)
        self.conda_name_entry = ctk.CTkEntry(input_frame, width=250)
        self.conda_name_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(input_frame, text="Python:").pack(side="left", padx=5)
        self.python_version = ctk.CTkOptionMenu(input_frame, values=["3.9", "3.10", "3.11", "3.12"])
        self.python_version.set("3.11")
        self.python_version.pack(side="left", padx=5)
        
        create_btn = ctk.CTkButton(input_frame, text="Crea", command=self.create_conda)
        create_btn.pack(side="left", padx=5)
        
        # Output console
        console_label = ctk.CTkLabel(tab, text="Console Output:", font=("Arial", 12, "bold"))
        console_label.pack(pady=(10, 5), padx=10, anchor="w")
        
        self.conda_console = ctk.CTkTextbox(tab, height=100, state="disabled")
        self.conda_console.pack(pady=5, padx=10, fill="both")
    
    def refresh_venv_list(self):
        """Refresh the list of Venv environments."""
        # Clear existing widgets
        for widget in self.venv_list_frame.winfo_children():
            widget.destroy()
        
        # Get list of venv environments
        venvs = self.list_venvs()
        
        if not venvs:
            label = ctk.CTkLabel(self.venv_list_frame, text="Nessun ambiente Venv trovato")
            label.pack(pady=5)
        else:
            for venv_name, venv_path in venvs:
                self.add_venv_entry(venv_name, venv_path)
    
    def refresh_conda_list(self):
        """Refresh the list of Conda environments."""
        # Clear existing widgets
        for widget in self.conda_list_frame.winfo_children():
            widget.destroy()
        
        # Get list of conda environments
        condas = self.list_conda_envs()
        
        if not condas:
            label = ctk.CTkLabel(self.conda_list_frame, text="Nessun ambiente Conda trovato (conda potrebbe non essere installato)")
            label.pack(pady=5)
        else:
            for conda_name in condas:
                self.add_conda_entry(conda_name)
    
    def add_venv_entry(self, name: str, path: str):
        """Add a venv entry to the list."""
        frame = ctk.CTkFrame(self.venv_list_frame)
        frame.pack(pady=2, padx=5, fill="x")

        label = ctk.CTkLabel(frame, text=f"{name} ({path})", anchor="w")
        label.pack(side="left", padx=5, fill="x", expand=True)

        select_btn = ctk.CTkButton(frame, text="Seleziona", width=100,
                                   command=lambda: self.select_environment("venv", name, path))
        select_btn.pack(side="left", padx=2)

        rename_btn = ctk.CTkButton(frame, text="Rinomina", width=100, fg_color="orange",
                                   command=lambda: self.rename_venv(name, path))
        rename_btn.pack(side="left", padx=2)

        clone_btn = ctk.CTkButton(frame, text="Clona", width=100, fg_color="purple",
                                  command=lambda: self.clone_venv(name, path))
        clone_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(frame, text="Elimina", width=100, fg_color="red",
                                   command=lambda: self.delete_venv(name, path))
        delete_btn.pack(side="left", padx=2)
    
    def add_conda_entry(self, name: str):
        """Add a conda entry to the list."""
        frame = ctk.CTkFrame(self.conda_list_frame)
        frame.pack(pady=2, padx=5, fill="x")
        
        label = ctk.CTkLabel(frame, text=name, anchor="w")
        label.pack(side="left", padx=5, fill="x", expand=True)
        
        select_btn = ctk.CTkButton(frame, text="Seleziona", width=100,
                                   command=lambda: self.select_environment("conda", name))
        select_btn.pack(side="left", padx=2)

        clone_btn = ctk.CTkButton(frame, text="Clona", width=100, fg_color="purple",
                                  command=lambda: self.clone_conda(name))
        clone_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(frame, text="Elimina", width=100, fg_color="red",
                                   command=lambda: self.delete_conda(name))
        delete_btn.pack(side="left", padx=2)
    
    def list_venvs(self) -> List[Tuple[str, str]]:
        """List all venv environments in multiple locations."""
        venvs = []

        # Check standard venv names in current directory
        standard_venv_names = ["venv", "env", ".venv", ".env", "virtualenv"]
        for venv_name in standard_venv_names:
            venv_path = Path(venv_name)
            if self._is_valid_venv(venv_path):
                venvs.append((venv_name, str(venv_path.absolute())))

        # Check .venvs directory for multiple environments
        venvs_dir = Path(".venvs")
        if venvs_dir.exists() and venvs_dir.is_dir():
            for item in venvs_dir.iterdir():
                if item.is_dir() and self._is_valid_venv(item):
                    venvs.append((f".venvs/{item.name}", str(item.absolute())))

        return venvs

    def _is_valid_venv(self, path: Path) -> bool:
        """Check if a path is a valid venv environment."""
        if not path.exists() or not path.is_dir():
            return False

        # Check for pyvenv.cfg
        pyvenv_cfg = path / "pyvenv.cfg"
        if not pyvenv_cfg.exists():
            return False

        # Check for Python executable
        if os.name == "nt":  # Windows
            python_exe = path / "Scripts" / "python.exe"
        else:  # Unix-like
            python_exe = path / "bin" / "python"

        return python_exe.exists()
    
    def list_conda_envs(self) -> List[str]:
        """List all conda environments."""
        # Try to find conda executable
        conda_exe = self.parent.find_conda_executable()
        if not conda_exe:
            return []

        try:
            result = subprocess.run(
                [conda_exe, "env", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                envs = []
                for env_path in data.get("envs", []):
                    env_name = Path(env_path).name
                    # Include all environments
                    envs.append(env_name)
                return envs
            else:
                return []
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            return []

    def create_venv(self):
        """Create a new venv environment."""
        name = self.venv_name_entry.get().strip()
        if not name:
            self.log_to_venv_console("Errore: Inserire un nome per l'ambiente\n")
            return
        
        venv_path = Path(".venvs") / name
        if venv_path.exists():
            self.log_to_venv_console(f"Errore: L'ambiente '{name}' esiste già\n")
            return
        
        # Create .venvs directory if it doesn't exist
        Path(".venvs").mkdir(exist_ok=True)
        
        self.log_to_venv_console(f"Creazione ambiente Venv '{name}' in corso...\n")
        
        # Create environment in a separate thread
        q = queue.Queue()
        thread = threading.Thread(target=self._create_venv_worker, args=(name, str(venv_path), q))
        thread.daemon = True
        thread.start()
        
        # Monitor the queue for output
        self.monitor_queue(q, self.venv_console, lambda: self.refresh_venv_list())
    
    def _create_venv_worker(self, name: str, path: str, q: queue.Queue):
        """Worker thread to create venv environment."""
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "venv", path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Read output line by line
            for line in process.stdout:
                q.put(line)
            
            process.wait()
            
            if process.returncode == 0:
                q.put(f"✓ Ambiente '{name}' creato con successo!\n")
            else:
                q.put(f"✗ Errore durante la creazione dell'ambiente (codice: {process.returncode})\n")
        except Exception as e:
            q.put(f"✗ Errore: {str(e)}\n")
        finally:
            q.put(None)  # Signal completion
    
    def create_conda(self):
        """Create a new conda environment."""
        name = self.conda_name_entry.get().strip()
        if not name:
            self.log_to_conda_console("Errore: Inserire un nome per l'ambiente\n")
            return
        
        python_ver = self.python_version.get()
        
        self.log_to_conda_console(f"Creazione ambiente Conda '{name}' con Python {python_ver}...\n")
        
        # Create environment in a separate thread
        q = queue.Queue()
        thread = threading.Thread(target=self._create_conda_worker, args=(name, python_ver, q))
        thread.daemon = True
        thread.start()
        
        # Monitor the queue for output
        self.monitor_queue(q, self.conda_console, lambda: self.refresh_conda_list())
    
    def _create_conda_worker(self, name: str, python_ver: str, q: queue.Queue):
        """Worker thread to create conda environment."""
        try:
            process = subprocess.Popen(
                ["conda", "create", "--name", name, f"python={python_ver}", "-y"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Read output line by line
            for line in process.stdout:
                q.put(line)
            
            process.wait()
            
            if process.returncode == 0:
                q.put(f"✓ Ambiente '{name}' creato con successo!\n")
            else:
                q.put(f"✗ Errore durante la creazione dell'ambiente (codice: {process.returncode})\n")
        except FileNotFoundError:
            q.put("✗ Errore: conda non trovato. Assicurarsi che Conda sia installato.\n")
        except Exception as e:
            q.put(f"✗ Errore: {str(e)}\n")
        finally:
            q.put(None)  # Signal completion
    
    def delete_venv(self, name: str, path: str):
        """Delete a venv environment."""
        if not messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare l'ambiente Venv '{name}'?\nQuesta azione non può essere annullata."):
            return

        self.log_to_venv_console(f"Eliminazione ambiente '{name}'...\n")
        try:
            shutil.rmtree(path)
            self.log_to_venv_console(f"✓ Ambiente '{name}' eliminato con successo!\n")
            self.refresh_venv_list()
        except Exception as e:
            self.log_to_venv_console(f"✗ Errore durante l'eliminazione: {str(e)}\n")

    def rename_venv(self, name: str, path: str):
        """Rename a venv environment."""
        new_name = simpledialog.askstring("Rinomina Ambiente", f"Inserisci nuovo nome per '{name}':", initialvalue=name)
        if not new_name or new_name.strip() == name:
            return

        new_name = new_name.strip()
        if not new_name:
            return

        # Check if new name already exists
        new_path = Path(path).parent / new_name
        if new_path.exists():
            messagebox.showerror("Errore", f"Un ambiente con nome '{new_name}' esiste già.")
            return

        # Rename
        try:
            Path(path).rename(new_path)
            self.log_to_venv_console(f"✓ Ambiente rinominato da '{name}' a '{new_name}'\n")
            self.refresh_venv_list()
        except Exception as e:
            self.log_to_venv_console(f"✗ Errore durante la rinominazione: {str(e)}\n")

    def clone_venv(self, name: str, path: str):
        """Clone a venv environment."""
        new_name = simpledialog.askstring("Clona Ambiente", f"Inserisci nome per la copia di '{name}':")
        if not new_name:
            return

        new_name = new_name.strip()
        if not new_name:
            return

        # Check if new name already exists
        new_path = Path(path).parent / new_name
        if new_path.exists():
            messagebox.showerror("Errore", f"Un ambiente con nome '{new_name}' esiste già.")
            return

        # Clone (copy directory)
        self.log_to_venv_console(f"Clonazione ambiente '{name}' in '{new_name}'...\n")
        try:
            shutil.copytree(path, str(new_path))
            self.log_to_venv_console(f"✓ Ambiente '{name}' clonato in '{new_name}'\n")
            self.refresh_venv_list()
        except Exception as e:
            self.log_to_venv_console(f"✗ Errore durante la clonazione: {str(e)}\n")

    def delete_conda(self, name: str):
        """Delete a conda environment."""
        if not messagebox.askyesno("Conferma Eliminazione", f"Sei sicuro di voler eliminare l'ambiente Conda '{name}'?\nQuesta azione non può essere annullata."):
            return

        self.log_to_conda_console(f"Eliminazione ambiente '{name}'...\n")

        q = queue.Queue()
        thread = threading.Thread(target=self._delete_conda_worker, args=(name, q))
        thread.daemon = True
        thread.start()

        self.monitor_queue(q, self.conda_console, lambda: self.refresh_conda_list())
    
    def _delete_conda_worker(self, name: str, q: queue.Queue):
        """Worker thread to delete conda environment."""
        try:
            process = subprocess.Popen(
                ["conda", "env", "remove", "--name", name, "-y"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                q.put(line)
            
            process.wait()
            
            if process.returncode == 0:
                q.put(f"✓ Ambiente '{name}' eliminato con successo!\n")
            else:
                q.put(f"✗ Errore durante l'eliminazione (codice: {process.returncode})\n")
        except Exception as e:
            q.put(f"✗ Errore: {str(e)}\n")
        finally:
            q.put(None)

    def clone_conda(self, name: str):
        """Clone a conda environment."""
        new_name = simpledialog.askstring("Clona Ambiente", f"Inserisci nome per la copia di '{name}':")
        if not new_name:
            return

        new_name = new_name.strip()
        if not new_name:
            return

        self.log_to_conda_console(f"Clonazione ambiente '{name}' in '{new_name}'...\n")

        q = queue.Queue()
        thread = threading.Thread(target=self._clone_conda_worker, args=(name, new_name, q))
        thread.daemon = True
        thread.start()

        self.monitor_queue(q, self.conda_console, lambda: self.refresh_conda_list())

    def _clone_conda_worker(self, name: str, new_name: str, q: queue.Queue):
        """Worker thread to clone conda environment."""
        try:
            process = subprocess.Popen(
                ["conda", "create", "--clone", name, "--name", new_name, "-y"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                q.put(line)

            process.wait()

            if process.returncode == 0:
                q.put(f"✓ Ambiente '{name}' clonato in '{new_name}'\n")
            else:
                q.put(f"✗ Errore durante la clonazione (codice: {process.returncode})\n")
        except Exception as e:
            q.put(f"✗ Errore: {str(e)}\n")
        finally:
            q.put(None)

    def monitor_queue(self, q: queue.Queue, console: ctk.CTkTextbox, completion_callback=None):
        """Monitor a queue and update the console with output."""
        try:
            while True:
                line = q.get_nowait()
                if line is None:  # Completion signal
                    if completion_callback:
                        completion_callback()
                    break
                self.log_to_console(console, line)
        except queue.Empty:
            # Schedule next check
            self.after(100, lambda: self.monitor_queue(q, console, completion_callback))

    def monitor_output_queue(self, q: queue.Queue):
        """Monitor the output queue (now using global log_queue)."""
        # Completion signal handled by _read_process_output
        pass



    def log_to_venv_console(self, message: str):
        """Log a message to the venv console."""
        self.log_to_console(self.venv_console, message)
    
    def log_to_conda_console(self, message: str):
        """Log a message to the conda console."""
        self.log_to_console(self.conda_console, message)
    
    def log_main_console(self, message: str):
        """Log a message to the main log console."""
        log_queue.put(message)

    def select_environment(self, env_type: str, name: str, path: str = None):
        """Select an environment and close the window."""
        self.callback(env_type, name, path)
        self.destroy()


class GitManager:
    """
    Gestisce tutte le operazioni Git, separando la logica dalla GUI.
    """
    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def _run_git_command(self, command: List[str]) -> Tuple[int, str, str]:
        """Esegue un comando git e restituisce (return_code, stdout, stderr)."""
        try:
            process = subprocess.run(
                ["git"] + command,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
                encoding='utf-8',
                errors='ignore'
            )
            return process.returncode, process.stdout.strip(), process.stderr.strip()
        except FileNotFoundError:
            return -1, "", "Git non trovato. Assicurarsi che sia installato e nel PATH."
        except Exception as e:
            return -1, "", f"Errore imprevisto: {e}"

    def is_git_repo(self) -> bool:
        """Verifica se il percorso è un repository Git valido."""
        return_code, _, _ = self._run_git_command(["rev-parse", "--is-inside-work-tree"])
        return return_code == 0

    def get_current_branch(self) -> Optional[str]:
        """Restituisce il nome del branch corrente."""
        ret, out, err = self._run_git_command(["branch", "--show-current"])
        return out if ret == 0 and out else "HEAD detached"

    def get_status(self) -> List[Dict[str, str]]:
        """Ottiene lo stato dei file (staged, unstaged, untracked)."""
        ret, out, err = self._run_git_command(["status", "--porcelain"])
        if ret != 0:
            return []

        files = []
        for line in out.split('\n'):
            if not line:
                continue
            status_code = line[:2]
            path = line[3:]

            staged_status = status_code[0]
            unstaged_status = status_code[1]

            file_info = {'path': path, 'staged': 'none', 'unstaged': 'none'}

            # Staged changes
            if staged_status == 'M': file_info['staged'] = 'Modified'
            elif staged_status == 'A': file_info['staged'] = 'Added'
            elif staged_status == 'D': file_info['staged'] = 'Deleted'
            elif staged_status == 'R': file_info['staged'] = 'Renamed'

            # Unstaged changes
            if unstaged_status == 'M': file_info['unstaged'] = 'Modified'
            elif unstaged_status == 'D': file_info['unstaged'] = 'Deleted'
            elif unstaged_status == '??': file_info['unstaged'] = 'Untracked'

            files.append(file_info)
        return files

    def get_commit_graph_data(self, max_commits=50) -> Tuple[List[Dict], Dict]:
        """
        Genera i dati per la visualizzazione del grafo dei commit.
        Implementa un algoritmo di layout per posizionare i commit in colonne.
        """
        # 1. Ottieni i dati grezzi dal log di git
        fmt = "%H|%P|%an|%s" # Hash|ParentHashes|Author|Subject
        ret, out, err = self._run_git_command(["log", "--all", f"--max-count={max_commits}", f"--pretty=format:{fmt}"])
        if ret != 0:
            return [], {}

        # 2. Costruisci una mappa dei nodi e identifica i figli di ogni commit
        nodes = {}
        all_children = {}
        lines = out.split('\n')
        for i, line in enumerate(lines):
            if not line: continue
            parts = line.split('|', 3)
            h, p, author, msg = parts
            parents = p.split()
            nodes[h] = {'y': i, 'parents': parents, 'hash': h, 'msg': msg, 'author': author, 'children': []}
            for parent_hash in parents:
                if parent_hash not in all_children:
                    all_children[parent_hash] = []
                all_children[parent_hash].append(h)

        for h, node in nodes.items():
            if h in all_children:
                node['children'] = all_children[h]

        # 3. Algoritmo di layout per assegnare le colonne (coordinate x)
        columns = {}
        lane_allocator = [None] * 20  # Supporta fino a 20 branch paralleli

        def find_free_lane(start_y):
            for i, last_y in enumerate(lane_allocator):
                if last_y is None or last_y > start_y:
                    return i
            return len(lane_allocator) # Fallback

        sorted_nodes = sorted(nodes.values(), key=lambda n: n['y'])

        for node in sorted_nodes:
            h = node['hash']
            y = node['y']

            if h in columns: # Già processato come parente
                continue

            # Se un figlio ha già una colonna, prova a ereditarla
            parent_of_lane = None
            for child_hash in node.get('children', []):
                if child_hash in columns:
                    child_col = columns[child_hash]
                    # Se il figlio è il primo del suo branch, eredita la colonna
                    if lane_allocator[child_col] == nodes[child_hash]['y']:
                        parent_of_lane = child_col
                        break

            if parent_of_lane is not None:
                col = parent_of_lane
            else:
                col = find_free_lane(y)

            columns[h] = col
            lane_allocator[col] = y

        # 4. Assegna le coordinate finali
        commit_list = []
        for h, node in nodes.items():
            node['x'] = columns.get(h, 0) * 40 + 30 # 40px per colonna, 30px di offset
            node['y'] = node['y'] * 70 + 40 # 70px per riga, 40px di offset
            commit_list.append(node)

        return commit_list, nodes

    # Funzioni di azione (stage, commit, push, etc.)
    def stage(self, files: List[str]) -> Tuple[bool, str]:
        ret, out, err = self._run_git_command(["add"] + files)
        return ret == 0, err

    def unstage(self, files: List[str]) -> Tuple[bool, str]:
        ret, out, err = self._run_git_command(["reset", "HEAD", "--"] + files)
        return ret == 0, err

    def commit(self, message: str) -> Tuple[bool, str]:
        ret, out, err = self._run_git_command(["commit", "-m", message])
        return ret == 0, out if ret == 0 else err

    def push(self) -> Tuple[bool, str]:
        ret, out, err = self._run_git_command(["push"])
        return ret == 0, out if ret == 0 else err

    def checkout(self, target: str) -> Tuple[bool, str]:
        ret, out, err = self._run_git_command(["checkout", target])
        return ret == 0, out if ret == 0 else err

    def create_branch(self, branch_name: str, from_commit: str) -> Tuple[bool, str]:
        ret, out, err = self._run_git_command(["branch", branch_name, from_commit])
        return ret == 0, out if ret == 0 else err

    def cherry_pick(self, commit_hash: str) -> Tuple[bool, str]:
        ret, out, err = self._run_git_command(["cherry-pick", commit_hash])
        return ret == 0, out if ret == 0 else err

    def merge(self, branch_name: str) -> Tuple[bool, str]:
        """Esegue il merge di un branch in quello corrente."""
        ret, out, err = self._run_git_command(["merge", branch_name])
        return ret == 0, out if ret == 0 else err

    def revert_commit(self, commit_hash: str) -> Tuple[bool, str]:
        """Esegue il revert di un commit specifico."""
        ret, out, err = self._run_git_command(["revert", "--no-edit", commit_hash])
        return ret == 0, out if ret == 0 else err

    def resume_operation(self) -> Tuple[bool, str, str]:
        """Tenta di riprendere un'operazione interrotta (merge/rebase)."""
        if (Path(self.repo_path) / ".git" / "MERGE_HEAD").exists():
            cmd = ["merge", "--continue"]
            op = "Merge"
        elif (Path(self.repo_path) / ".git" / "rebase-apply").exists():
            cmd = ["rebase", "--continue"]
            op = "Rebase"
        else:
            return False, "Nessuna operazione da riprendere", ""

        ret, out, err = self._run_git_command(cmd)
        return ret == 0, out if ret == 0 else err, op

    def get_all_refresh_data(self, max_commits=50) -> Dict:
        """
        Raccoglie tutti i dati necessari per un refresh della UI in un'unica operazione.
        Questa funzione è pensata per essere eseguita in un thread separato.
        """
        if not self.is_git_repo():
            return {"is_repo": False}

        status_files = self.get_status()
        commits, nodes_map = self.get_commit_graph_data(max_commits)
        current_branch = self.get_current_branch()

        return {
            "is_repo": True,
            "branch": current_branch,
            "status_files": status_files,
            "commits": commits,
            "nodes_map": nodes_map,
        }


class GitOperationManager:
    """Gestisce operazioni Git asincrone per evitare blocco della GUI."""

    def __init__(self, git_manager, ui_callback):
        self.git_manager = git_manager
        self.ui_callback = ui_callback
        self.active_operations = set()
        self.operation_queue = queue.Queue()
        self.cancel_requested = False
        self.cancel_requested_for = None  # Traccia quale operazione è stata richiesta per cancellazione

    def execute_async(self, operation_name: str, operation_func, *args, **kwargs):
        """Esegue un'operazione Git in un thread separato."""
        if operation_name in self.active_operations:
            # Operazione già in corso, ignora
            return

        self.active_operations.add(operation_name)
        self.cancel_requested = False

        # Notifica UI che l'operazione è iniziata
        self.ui_callback.on_git_operation_started(operation_name)

        def worker():
            try:
                result = operation_func(*args, **kwargs)

                # Se l'operazione è stata annullata, chiama la callback di annullamento, altrimenti quella di completamento
                if self.cancel_requested and self.cancel_requested_for == operation_name:
                    self.ui_callback.after(0, lambda: self.ui_callback.on_git_operation_cancelled(operation_name))
                else:
                    self.ui_callback.after(0, lambda: self.ui_callback.on_git_operation_completed(operation_name, result))

            except Exception as e:
                # Se c'è un errore, gestiscilo, indipendentemente dalla cancellazione
                self.ui_callback.after(0, lambda: self.ui_callback.on_git_operation_error(operation_name, str(e)))
            finally:
                self.active_operations.discard(operation_name)
                if self.cancel_requested_for == operation_name:
                    self.cancel_requested = False
                    self.cancel_requested_for = None

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def cancel_operation(self, operation_name: str):
        """Richiesta cancellazione operazione con feedback onesto."""
        if operation_name in self.active_operations:
            self.cancel_requested = True
            self.cancel_requested_for = operation_name
            self.ui_callback.on_git_operation_cancel_requested(operation_name)
            # NON chiamare on_git_operation_cancelled immediatamente - aspetta che termini naturalmente

    def is_operation_active(self, operation_name: str) -> bool:
        """Verifica se un'operazione è attualmente attiva."""
        return operation_name in self.active_operations


class App(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Universal Starter GUI")
        self.geometry("1200x700")
        
        # Application state
        self.env_type = None  # "venv", "conda", or "system"
        self.env_name = None
        self.env_path = None
        self.conda_exe = None  # Path to conda executable
        self.files = []  # List of {"name": str, "path": str, "process": subprocess.Popen, "status": str}
        self.config_file = "config_STARTER_GUI.json"
        self.current_tab = None  # Track current tab for change detection

        # NUOVA RIGA: Inizializza il GitManager
        self.git_manager = GitManager(os.getcwd())

        # Inizializza il GitOperationManager per operazioni asincrone
        self.git_op_manager = GitOperationManager(self.git_manager, self)

        # Setup GUI
        self.setup_gui()

        # Load configuration
        self.load_config()
        
        # Update status periodically
        self.update_process_status()

        # Monitor log queue
        self.monitor_log_queue()
    
    def setup_gui(self):
        """Setup the main GUI."""
        # Crea tabview principale con la command per il cambio tab
        self.tabview = ctk.CTkTabview(self, width=1200, height=700, command=self.on_tab_change)
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        # Tab Main (contenuto esistente)
        self.tabview.add("Main")
        main_tab = self.tabview.tab("Main")

        # Environment section
        env_frame = ctk.CTkFrame(main_tab)
        env_frame.pack(pady=10, padx=10, fill="x")

        # Configure grid for env_frame
        env_frame.grid_columnconfigure(1, weight=1)

        # Top row: Environment info
        ctk.CTkLabel(env_frame, text="Ambiente Attivo:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=5, sticky="w")

        self.env_label = ctk.CTkLabel(env_frame, text="Nessun ambiente selezionato",
                                      font=("Arial", 12), text_color="gray")
        self.env_label.grid(row=0, column=1, padx=5, sticky="ew")

        # Bottom row: Action buttons
        buttons_frame = ctk.CTkFrame(env_frame)
        buttons_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        manage_btn = ctk.CTkButton(buttons_frame, text="Gestisci Ambienti",
                                   command=self.open_env_manager)
        manage_btn.pack(side="left", padx=5)

        install_deps_btn = ctk.CTkButton(buttons_frame, text="Installa Dipendenze",
                                        command=self.install_dependencies)
        install_deps_btn.pack(side="left", padx=5)

        verify_libs_btn = ctk.CTkButton(buttons_frame, text="Verifica Librerie",
                                        command=self.verify_libraries)
        verify_libs_btn.pack(side="left", padx=5)

        editor_req_btn = ctk.CTkButton(buttons_frame, text="Editor Requirements",
                                       command=self.open_requirements_editor)
        editor_req_btn.pack(side="left", padx=5)

        test_cuda_btn = ctk.CTkButton(buttons_frame, text="Test CUDA/PyTorch",
                                      command=self.test_cuda_pytorch)
        test_cuda_btn.pack(side="left", padx=5)

        process_btn = ctk.CTkButton(buttons_frame, text="Processi Localhost",
                                   command=self.show_process_viewer)
        process_btn.pack(side="left", padx=5)

        # Files section
        files_label = ctk.CTkLabel(main_tab, text="File da Avviare:", font=("Arial", 14, "bold"))
        files_label.pack(pady=(10, 5), padx=10, anchor="w")

        # Scrollable frame for files
        self.files_frame = ctk.CTkScrollableFrame(main_tab, height=300)
        self.files_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # Add file button
        add_file_btn = ctk.CTkButton(main_tab, text="➕ Aggiungi File", command=self.add_file)
        add_file_btn.pack(pady=5)

        # Shell launch option
        self.shell_checkbox = ctk.CTkCheckBox(main_tab, text="Lancia in nuova shell")
        self.shell_checkbox.pack(pady=5)

        # Control buttons
        control_frame = ctk.CTkFrame(main_tab)
        control_frame.pack(pady=10, padx=10, fill="x")

        start_all_btn = ctk.CTkButton(control_frame, text="▶ Avvia Tutti",
                                      command=self.start_all, fg_color="green")
        start_all_btn.pack(side="left", padx=5, expand=True, fill="x")

        stop_all_btn = ctk.CTkButton(control_frame, text="⏹ Ferma Tutti",
                                     command=self.stop_all, fg_color="red")
        stop_all_btn.pack(side="left", padx=5, expand=True, fill="x")

        save_btn = ctk.CTkButton(control_frame, text="💾 Salva Configurazione",
                                command=self.save_config)
        save_btn.pack(side="left", padx=5, expand=True, fill="x")

        # Log output section
        log_label = ctk.CTkLabel(main_tab, text="Log Output:", font=("Arial", 14, "bold"))
        log_label.pack(pady=(10, 5), padx=10, anchor="w")

        self.log_console = ctk.CTkTextbox(main_tab, height=150, state="disabled")
        self.log_console.pack(pady=5, padx=10, fill="both", expand=True)

        # Tab Git Status
        self.tabview.add("Git Status")
        git_tab = self.tabview.tab("Git Status")

        # Header per git status
        git_header = ctk.CTkFrame(git_tab)
        git_header.pack(pady=5, padx=10, fill="x")
        self.git_branch_label = ctk.CTkLabel(git_header, text="Branch: N/A")
        self.git_branch_label.pack(side="left", padx=(0, 10))

        # Configurazione limite commit
        ctk.CTkLabel(git_header, text="Commit da mostrare:").pack(side="left")
        self.git_commit_limit_entry = ctk.CTkEntry(git_header, width=50)
        self.git_commit_limit_entry.insert(0, "50")
        self.git_commit_limit_entry.pack(side="left", padx=5)

        refresh_git_btn = ctk.CTkButton(git_header, text="Aggiorna", command=self.refresh_git_status_async)
        refresh_git_btn.pack(side="right")

        # Scrollable frame per file git
        self.git_files_frame = ctk.CTkScrollableFrame(git_tab, height=200)
        self.git_files_frame.pack(pady=5, padx=10, fill="x")

        # Pulsanti per staging
        stage_frame = ctk.CTkFrame(git_tab)
        stage_frame.pack(pady=5, padx=10, fill="x")
        self.stage_selected_btn = ctk.CTkButton(stage_frame, text="Stage Selezionati", command=self.stage_selected_files)
        self.stage_selected_btn.pack(side="left", padx=5)
        self.unstage_selected_btn = ctk.CTkButton(stage_frame, text="Unstage Selezionati", command=self.unstage_selected_files)
        self.unstage_selected_btn.pack(side="left", padx=5)

        # Sezione grafico branch
        graph_label = ctk.CTkLabel(git_tab, text="Grafico Branch:", font=("Arial", 12, "bold"))
        graph_label.pack(pady=(10, 5), padx=10, anchor="w")
        # Frame per canvas e scrollbar
        canvas_frame = ctk.CTkFrame(git_tab)
        canvas_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self.git_graph_canvas = ctk.CTkCanvas(canvas_frame, bg="gray20", highlightthickness=0)

        # Scrollbar Verticale
        v_scrollbar = ctk.CTkScrollbar(canvas_frame, command=self.git_graph_canvas.yview)
        v_scrollbar.pack(side="right", fill="y")

        # Scrollbar Orizzontale
        h_scrollbar = ctk.CTkScrollbar(canvas_frame, command=self.git_graph_canvas.xview, orientation="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")

        self.git_graph_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.git_graph_canvas.pack(side="left", fill="both", expand=True)

        # Pulsanti azioni git
        actions_frame = ctk.CTkFrame(git_tab)
        actions_frame.pack(pady=10, padx=10, fill="x")
        self.commit_btn = ctk.CTkButton(actions_frame, text="Commit", command=self.git_commit, state="disabled")
        self.commit_btn.pack(side="left", padx=5)
        self.push_btn = ctk.CTkButton(actions_frame, text="Push", command=self.git_push, state="disabled")
        self.push_btn.pack(side="left", padx=5)
        self.merge_btn = ctk.CTkButton(actions_frame, text="Merge", command=self.git_merge, state="disabled")
        self.merge_btn.pack(side="left", padx=5)
        self.revert_btn = ctk.CTkButton(actions_frame, text="Revert", command=self.git_revert, state="disabled")
        self.revert_btn.pack(side="left", padx=5)
        self.resume_btn = ctk.CTkButton(actions_frame, text="Resume", command=self.git_resume, state="disabled")
        self.resume_btn.pack(side="left", padx=5)

        # Indicatori di progresso e stato per operazioni Git
        self.git_progress_frame = ctk.CTkFrame(git_tab)
        self.git_progress_frame.pack(pady=5, padx=10, fill="x")

        self.git_status_label = ctk.CTkLabel(self.git_progress_frame, text="", font=("Arial", 10))
        self.git_status_label.pack(side="left", padx=5)

        self.git_progress_bar = ctk.CTkProgressBar(self.git_progress_frame, width=200)
        self.git_progress_bar.pack(side="right", padx=5)
        self.git_progress_bar.set(0)  # Inizialmente nascosto

        self.git_cancel_btn = ctk.CTkButton(self.git_progress_frame, text="Annulla", command=self.cancel_git_operation, state="disabled")
        self.git_cancel_btn.pack(side="right", padx=5)

        # Aggiungi tooltip
        self.create_tooltip(self.commit_btn, "Crea un nuovo commit con i file attualmente staged.")
        self.create_tooltip(self.push_btn, "Invia i commit locali al repository remoto.")
        self.create_tooltip(self.merge_btn, "Unisci un branch selezionato nel branch corrente.")
        self.create_tooltip(self.revert_btn, "Annulla le modifiche di un commit specifico.")
        self.create_tooltip(self.resume_btn, "Riprendi un'operazione interrotta (merge/rebase).")
        self.create_tooltip(self.stage_selected_btn, "Aggiungi i file selezionati all'area di staging.")
        self.create_tooltip(self.unstage_selected_btn, "Rimuovi i file selezionati dall'area di staging.")

        # ==================================================
        # NUOVA SEZIONE: Tab Help
        # ==================================================
        self.tabview.add("Help")
        help_tab = self.tabview.tab("Help")

        help_frame = ctk.CTkScrollableFrame(help_tab)
        help_frame.pack(fill="both", expand=True, padx=10, pady=10)

        help_text = """
Benvenuto in Universal Starter GUI!
Questa applicazione ti aiuta a gestire e lanciare i tuoi script,
con un supporto integrato per ambienti virtuali Python e Git.

--- Sezione Main ---

Ambiente Attivo:
Mostra l'ambiente Python (Venv/Conda) attualmente selezionato.
• Gestisci Ambienti: Apre una finestra per creare, eliminare, clonare e selezionare ambienti Venv o Conda.
• Installa Dipendenze: Installa le librerie da un file `requirements.txt` nell'ambiente attivo.
• Verifica Librerie: Mostra un elenco di tutte le librerie installate nell'ambiente attivo.
• Editor Requirements: Apre un semplice editor di testo per creare o modificare file `requirements.txt`.
• Test CUDA/PyTorch: Esegue un test per verificare se PyTorch è installato e se rileva correttamente la GPU (CUDA).
• Processi Localhost: Mostra i processi attivi sulla tua macchina che sono in ascolto su porte locali (es. web server).

File da Avviare:
Elenco degli script che vuoi gestire.
• ➕ Aggiungi File: Seleziona uno script Python (.py) o un eseguibile da aggiungere alla lista.
• ▶ (Avvia): Esegue lo script selezionato. L'output verrà mostrato nella console "Log Output".
• ⏹ (Ferma): Termina il processo dello script.
• 🗑 (Rimuovi): Rimuove lo script dalla lista.
• Lancia in nuova shell: Se spuntato, gli script verranno eseguiti in una nuova finestra del terminale anziché all'interno dell'app.

Controlli Globali:
• Avvia Tutti / Ferma Tutti: Esegue o termina tutti gli script nella lista.
• Salva Configurazione: Salva l'ambiente attivo e la lista di file nel file `config_STARTER_GUI.json` per caricarli al prossimo avvio.

--- Sezione Git Status ---

Questa sezione fornisce un'interfaccia visuale per il tuo repository Git.

Grafico dei Branch:
• Visualizzazione ad Albero: Mostra la storia dei commit come un grafo. Ogni colonna verticale rappresenta una linea di sviluppo (branch).
• Commit Cliccabili: Clicca su un commit (il cerchio colorato) per aprire un menu con azioni rapide:
  - Checkout: Spostati a quel commit (entrerai in stato "detached HEAD").
  - Crea branch da...: Crea un nuovo branch a partire da quel commit.
  - Cherry-pick: Applica le modifiche di quel commit sul tuo branch attuale.
  - Copia Hash: Copia l'hash completo del commit negli appunti.

Stato dei File:
Mostra i file che sono stati modificati, aggiunti o eliminati.
• Seleziona i file usando le checkbox a sinistra.
• Stage Selezionati: Aggiunge i file selezionati all'area di staging, pronti per il prossimo commit.
• Unstage Selezionati: Rimuove i file selezionati dall'area di staging.

Azioni Git:
• Commit: Crea un nuovo salvataggio (commit) con i file che hai messo in "stage". Ti chiederà un messaggio di commit.
• Push: Invia i tuoi commit locali al repository remoto (es. GitHub).
"""

        help_label = ctk.CTkLabel(help_frame, text=help_text, justify="left", anchor="w")
        help_label.pack(padx=10, pady=10, fill="x")

# Fine della funzione setup_gui

        # Inizializza status git
        self.refresh_git_status_async()

        # Start auto-refresh for git status
        self.start_git_auto_refresh()

    def on_tab_change(self):
        """Handle tab change to refresh git status when Git Status tab is selected."""
        if self.tabview.get() == "Git Status":
            self.refresh_git_status_async()

    def create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget."""
        tooltip_label = None
        def show_tooltip(event):
            nonlocal tooltip_label
            if tooltip_label:
                tooltip_label.destroy()
            tooltip_label = tk.Label(self, text=text, bg="yellow", relief="solid", borderwidth=1, font=("Arial", 8))
            tooltip_label.place(x=event.x + widget.winfo_x() + 10, y=event.y + widget.winfo_y() + 20)
        def hide_tooltip(event):
            nonlocal tooltip_label
            if tooltip_label:
                tooltip_label.destroy()
                tooltip_label = None
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def open_env_manager(self):
        """Open the environment manager window."""
        EnvManagerWindow(self, self.on_environment_selected)

    def open_requirements_editor(self):
        """Open the requirements editor window."""
        RequirementsEditor(self)

    def show_process_viewer(self):
        """Open the localhost process viewer window."""
        ProcessViewer(self)

    def install_dependencies(self, req_file=None):
        """Install dependencies from requirements.txt in the selected environment."""
        if not self.env_type:
            messagebox.showerror("Errore", "Selezionare un ambiente prima di installare dipendenze.")
            return

        if not req_file:
            req_file = ctk.filedialog.askopenfilename(
                title="Seleziona requirements.txt",
                filetypes=[("Requirements", "requirements.txt"), ("Text Files", "*.txt"), ("All Files", "*.*")]
            )

            if not req_file:
                return

        log_queue.put(f"Installazione dipendenze da {req_file} nell'ambiente {self.env_name}...\n")

        # Build pip command
        if self.env_type == "conda":
            command = [self.conda_exe or "conda", "run", "-n", self.env_name, "pip", "install", "-r", req_file]
        elif self.env_type == "venv":
            if os.name == "nt":  # Windows
                python_exe = os.path.join(self.env_path, "Scripts", "python.exe")
            else:  # Unix-like
                python_exe = os.path.join(self.env_path, "bin", "python")
            command = [python_exe, "-m", "pip", "install", "-r", req_file]
        else:
            log_queue.put("Errore: Tipo ambiente non supportato per installazione dipendenze.\n")
            return

        # Validate command
        if not self._validate_command(command):
            return

        # Log command
        log_queue.put(f"Eseguendo comando: {' '.join(command)}\n")

        # Run installation in a thread
        q = queue.Queue()
        thread = threading.Thread(target=run_install_command, args=(command, q))
        thread.daemon = True
        thread.start()

        monitor_install_queue(q, self)

    def verify_libraries(self):
        """Verify installed libraries in the selected environment."""
        if not self.env_type:
            messagebox.showerror("Errore", "Selezionare un ambiente prima di verificare le librerie.")
            return

        # Create popup window
        popup = ctk.CTkToplevel(self)
        popup.title(f"Librerie in {self.env_name}")
        popup.geometry("600x400")
        popup.transient(self)
        popup.grab_set()

        # Textbox for output
        text = ctk.CTkTextbox(popup, wrap="word")
        text.pack(pady=10, padx=10, fill="both", expand=True)

        # Build command
        if self.env_type == "conda":
            command = [self.conda_exe or "conda", "run", "-n", self.env_name, "pip", "list"]
        elif self.env_type == "venv":
            if os.name == "nt":  # Windows
                python_exe = os.path.join(self.env_path, "Scripts", "python.exe")
            else:  # Unix-like
                python_exe = os.path.join(self.env_path, "bin", "python")
            command = [python_exe, "-m", "pip", "list"]
        else:
            text.insert("end", "Tipo ambiente non supportato.\n")
            return

        # Validate command
        if not self._validate_command(command):
            text.insert("end", "Errore: Impossibile trovare l'eseguibile necessario.\n")
            return

        # Log command
        log_queue.put(f"Verifica librerie: {' '.join(command)}\n")

        # Run command in thread
        q = queue.Queue()
        thread = threading.Thread(target=self._run_verify_command, args=(command, q))
        thread.daemon = True
        thread.start()

        # Monitor queue
        self._monitor_verify_queue(q, text)

    def _run_verify_command(self, command: List[str], q: queue.Queue):
        """Run the verify command and put output into queue."""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                q.put(line)

            process.wait()

            if process.returncode != 0:
                q.put(f"Errore (codice: {process.returncode})\n")
        except Exception as e:
            q.put(f"Errore: {str(e)}\n")
        finally:
            q.put(None)

    def _monitor_verify_queue(self, q: queue.Queue, text: ctk.CTkTextbox):
        """Monitor the verify output queue."""
        try:
            while True:
                line = q.get_nowait()
                if line is None:
                    break
                if text.winfo_exists():
                    text.insert("end", line)
                    text.see("end")
        except queue.Empty:
            if text.winfo_exists():
                self.after(100, lambda: self._monitor_verify_queue(q, text))

    def _validate_command(self, command: List[str]) -> bool:
        """Validate that the command executable exists."""
        exe = command[0]
        if exe in ["conda", self.conda_exe]:
            # Check if conda is available
            if not (self.conda_exe or shutil.which("conda")):
                log_queue.put("Errore: Conda non trovato. Assicurati che Conda sia installato e nel PATH.\n")
                return False
        else:
            # Check if file exists
            if not os.path.exists(exe):
                log_queue.put(f"Errore: Eseguibile non trovato: {exe}\n")
                return False
        return True

    def test_cuda_pytorch(self):
        """Test CUDA and PyTorch in the selected environment."""
        if not self.env_type:
            messagebox.showerror("Errore", "Selezionare un ambiente prima di testare CUDA/PyTorch.")
            return

        # Create popup window
        popup = ctk.CTkToplevel(self)
        popup.title(f"Test CUDA/PyTorch in {self.env_name}")
        popup.geometry("600x400")
        popup.transient(self)
        popup.grab_set()

        # Textbox for output
        text = ctk.CTkTextbox(popup, wrap="word")
        text.pack(pady=10, padx=10, fill="both", expand=True)

        # Test script
        test_script = """import sys
try:
    import torch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    else:
        print("CUDA not available")
except ImportError as e:
    print(f"PyTorch not installed: {e}")
except Exception as e:
    print(f"Error: {e}")
"""

        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(test_script)
            temp_file = f.name

        # Build command
        if self.env_type == "conda":
            command = [self.conda_exe or "conda", "run", "-n", self.env_name, "python", temp_file]
        elif self.env_type == "venv":
            if os.name == "nt":  # Windows
                python_exe = os.path.join(self.env_path, "Scripts", "python.exe")
            else:  # Unix-like
                python_exe = os.path.join(self.env_path, "bin", "python")
            command = [python_exe, temp_file]
        else:
            text.insert("end", "Tipo ambiente non supportato.\n")
            os.unlink(temp_file)
            return

        # Validate command
        if not self._validate_command(command):
            text.insert("end", "Errore: Impossibile trovare l'eseguibile necessario.\n")
            os.unlink(temp_file)
            return

        # Log command
        log_queue.put(f"Test CUDA/PyTorch: {' '.join(command)}\n")

        # Run command in thread
        q = queue.Queue()
        thread = threading.Thread(target=self._run_test_command, args=(command, temp_file, q))
        thread.daemon = True
        thread.start()

        # Monitor queue
        self._monitor_verify_queue(q, text)

    def _run_test_command(self, command: List[str], temp_file: str, q: queue.Queue):
        """Run the test command and put output into queue, then clean up temp file."""
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                q.put(line)

            process.wait()

            if process.returncode != 0:
                q.put(f"Errore (codice: {process.returncode})\n")
        except Exception as e:
            q.put(f"Errore: {str(e)}\n")
        finally:
            q.put(None)
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass

    def on_environment_selected(self, env_type: str, name: str, path: str = None):
        """Callback when an environment is selected."""
        self.env_type = env_type
        self.env_name = name
        self.env_path = path

        if env_type == "conda":
            self.conda_exe = self.find_conda_executable()
            if not self.conda_exe and not shutil.which("conda"):
                messagebox.showwarning("Avviso", "Conda non trovato nel PATH. Alcune funzionalità potrebbero non funzionare.")

        if env_type == "venv":
            # Validate venv python executable
            if os.name == "nt":  # Windows
                python_exe = os.path.join(path, "Scripts", "python.exe")
            else:  # Unix-like
                python_exe = os.path.join(path, "bin", "python")
            if not os.path.exists(python_exe):
                messagebox.showwarning("Avviso", f"Python eseguibile non trovato in {python_exe}. L'ambiente potrebbe non essere valido.")
                self.env_label.configure(text=f"Venv: {name} ({path}) - INVALIDO", text_color="red")
            else:
                self.env_label.configure(text=f"Venv: {name} ({path})", text_color="green")
        elif env_type == "conda":
            self.env_label.configure(text=f"Conda: {name}", text_color="blue")
        
        self.save_config()
    
    def add_file(self):
        """Add a new file to the list."""
        file_path = ctk.filedialog.askopenfilename(
            title="Seleziona File",
            filetypes=[("Python Scripts", "*.py"), ("Executables", "*.exe"), ("All Files", "*.*")]
        )
        
        if file_path:
            file_name = Path(file_path).name
            
            # Check if file already exists
            if any(f["path"] == file_path for f in self.files):
                return
            
            file_entry = {
                "name": file_name,
                "path": file_path,
                "process": None,
                "status": "stopped"
            }
            
            self.files.append(file_entry)
            self.add_file_widget(len(self.files) - 1)
            self.save_config()
    
    def add_file_widget(self, index: int):
        """Add a file widget to the GUI."""
        file_entry = self.files[index]
        
        frame = ctk.CTkFrame(self.files_frame)
        frame.pack(pady=5, padx=5, fill="x")
        
        # Status indicator
        status_label = ctk.CTkLabel(frame, text="⚫", font=("Arial", 20), width=30)
        status_label.pack(side="left", padx=5)
        file_entry["status_label"] = status_label
        
        # File info
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        name_label = ctk.CTkLabel(info_frame, text=file_entry["name"], 
                                  font=("Arial", 12, "bold"), anchor="w")
        name_label.pack(fill="x")
        
        path_label = ctk.CTkLabel(info_frame, text=file_entry["path"], 
                                  font=("Arial", 9), anchor="w", text_color="gray")
        path_label.pack(fill="x")
        
        # Control buttons
        start_btn = ctk.CTkButton(frame, text="▶", width=40, 
                                 command=lambda: self.start_file(index))
        start_btn.pack(side="left", padx=2)
        file_entry["start_btn"] = start_btn
        
        stop_btn = ctk.CTkButton(frame, text="⏹", width=40, fg_color="red",
                                command=lambda: self.stop_file(index))
        stop_btn.pack(side="left", padx=2)
        file_entry["stop_btn"] = stop_btn
        
        remove_btn = ctk.CTkButton(frame, text="🗑", width=40, fg_color="darkred",
                                  command=lambda: self.remove_file(index))
        remove_btn.pack(side="left", padx=2)
    
    def start_file(self, index: int):
        """Start a file."""
        file_entry = self.files[index]
        
        if file_entry["process"] and file_entry["process"].poll() is None:
            return  # Already running
        
        file_path = file_entry["path"]
        
        # Build command based on environment type
        command = self.build_command(file_path)

        try:
            if self.shell_checkbox.get():
                # Launch in external terminal
                terminal_command = self.build_terminal_command(command)
                process = subprocess.Popen(
                    terminal_command,
                    shell=False  # Already handled in command
                )
                file_entry["process"] = process
                file_entry["status"] = "running"
                self.update_file_status(index)
                # No output reading for external terminal
                log_queue.put(f"[{file_entry['name']}] Avviato in terminale esterno\n")
            else:
                # Normal launch with output capture
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=False
                )

                file_entry["process"] = process
                file_entry["status"] = "running"
                self.update_file_status(index)

                # Start thread to read output
                q = queue.Queue()
                thread = threading.Thread(target=read_process_output, args=(process, q, file_entry["name"]))
                thread.daemon = True
                thread.start()

                # Log handled by global log_queue
        except Exception as e:
            log_queue.put(f"Errore avvio {file_entry['name']}: {e}\n")
            file_entry["status"] = "error"
            self.update_file_status(index)
    
    def stop_file(self, index: int):
        """Stop a file."""
        file_entry = self.files[index]
        
        if file_entry["process"]:
            try:
                file_entry["process"].terminate()
                file_entry["process"].wait(timeout=5)
            except subprocess.TimeoutExpired:
                file_entry["process"].kill()
            
            file_entry["process"] = None
            file_entry["status"] = "stopped"
            self.update_file_status(index)
    
    def remove_file(self, index: int):
        """Remove a file from the list."""
        # Stop process if running
        self.stop_file(index)
        
        # Remove from list
        self.files.pop(index)
        
        # Rebuild GUI
        for widget in self.files_frame.winfo_children():
            widget.destroy()
        
        for i in range(len(self.files)):
            self.add_file_widget(i)
        
        self.save_config()
    
    def start_all(self):
        """Start all files."""
        for i in range(len(self.files)):
            self.start_file(i)
    
    def stop_all(self):
        """Stop all files."""
        for i in range(len(self.files)):
            self.stop_file(i)
    
    def build_command(self, script_path: str) -> List[str]:
        """Build the command to run a script based on the active environment."""
        if self.env_type == "conda" and self.env_name:
            if self.conda_exe:
                return [self.conda_exe, "run", "-n", self.env_name, "python", script_path]
            else:
                # Fallback to system if conda not found
                return [sys.executable, script_path]
        elif self.env_type == "venv" and self.env_path:
            if os.name == "nt":  # Windows
                python_exe = os.path.join(self.env_path, "Scripts", "python.exe")
            else:  # Unix-like
                python_exe = os.path.join(self.env_path, "bin", "python")
            return [python_exe, script_path]
        else:
            # System Python or executable
            if script_path.endswith(".py"):
                return [sys.executable, script_path]
            else:
                return [script_path]

    def build_terminal_command(self, command: List[str]) -> List[str]:
        """Build command to launch in external terminal."""
        if os.name == "nt":  # Windows
            # Use 'start cmd /k' to open cmd window and keep it open
            return ["cmd", "/c", "start", "cmd", "/k"] + [" ".join(command)]
        else:  # Unix-like
            # Try common terminals
            terminals = ["xterm", "gnome-terminal", "konsole", "xfce4-terminal"]
            for term in terminals:
                if shutil.which(term):
                    if term == "gnome-terminal":
                        return [term, "--"] + command
                    else:
                        return [term, "-e"] + command
            # Fallback to shell
            return ["sh", "-c"] + [" ".join(command)]

    def update_file_status(self, index: int):
        """Update the status indicator for a file."""
        if index >= len(self.files):
            return
        
        file_entry = self.files[index]
        status_label = file_entry.get("status_label")
        
        if not status_label:
            return
        
        if file_entry["status"] == "running":
            status_label.configure(text="🟢", text_color="green")
        elif file_entry["status"] == "error":
            status_label.configure(text="🔴", text_color="red")
        else:
            status_label.configure(text="⚫", text_color="gray")
    
    def update_process_status(self):
        """Periodically update the status of all processes."""
        for i, file_entry in enumerate(self.files):
            if file_entry["process"]:
                if file_entry["process"].poll() is not None:
                    # Process has terminated
                    file_entry["process"] = None
                    file_entry["status"] = "stopped"
                    self.update_file_status(i)
        
        # Schedule next update
        self.after(1000, self.update_process_status)

    def find_conda_executable(self) -> Optional[str]:
        """Find the conda executable path."""
        # Check common locations
        possible_paths = [
            os.environ.get("CONDA_EXE"),
            "conda",  # In PATH
            "/opt/anaconda3/bin/conda",
            "/opt/miniconda3/bin/conda",
            "C:\\ProgramData\\Anaconda3\\Scripts\\conda.exe",
            "C:\\ProgramData\\Miniconda3\\Scripts\\conda.exe",
        ]
        for path in possible_paths:
            if path and shutil.which(path):
                return path
        return None

    def monitor_log_queue(self):
        """Monitor the global log queue and update the console."""
        try:
            while True:
                message = log_queue.get_nowait()
                if hasattr(self, 'log_console') and self.log_console:
                    log_to_console(self.log_console, message)
                else:
                    print(message.strip())
        except queue.Empty:
            pass
        # Schedule next check
        self.after(100, self.monitor_log_queue)

    def save_config(self):
        """Save configuration to JSON file."""
        config = {
            "environment": {
                "type": self.env_type,
                "name": self.env_name,
                "path": self.env_path
            },
            "files": [
                {
                    "name": f["name"],
                    "path": f["path"]
                }
                for f in self.files
            ]
        }
        
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def load_config(self):
        """Load configuration from JSON file."""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Load environment
            env = config.get("environment", {})
            self.env_type = env.get("type")
            self.env_name = env.get("name")
            self.env_path = env.get("path")
            
            if self.env_type and self.env_name:
                if self.env_type == "venv":
                    self.env_label.configure(text=f"Venv: {self.env_name} ({self.env_path})", 
                                           text_color="green")
                elif self.env_type == "conda":
                    self.env_label.configure(text=f"Conda: {self.env_name}", 
                                           text_color="blue")
            
            # Load files
            for file_data in config.get("files", []):
                file_entry = {
                    "name": file_data["name"],
                    "path": file_data["path"],
                    "process": None,
                    "status": "stopped"
                }
                self.files.append(file_entry)
                self.add_file_widget(len(self.files) - 1)
        except Exception as e:
            print(f"Error loading config: {e}")

    def refresh_git_status_async(self):
        """Esegue il refresh completo dei dati Git in modo asincrono."""
        if self.git_op_manager.is_operation_active("refresh"):
            return  # Evita refresh multipli

        try:
            limit = int(self.git_commit_limit_entry.get())
        except (ValueError, TypeError):
            limit = 50  # Fallback

        # Esegui la vera funzione di caricamento dati in background
        self.git_op_manager.execute_async("refresh", self.git_manager.get_all_refresh_data, max_commits=limit)

    def refresh_git_status(self, data: Dict):
        """
        DISEGNA lo stato di Git sulla UI usando i dati pre-caricati.
        Questa funzione è veloce e non bloccante.
        """
        # Clear existing file widgets
        for widget in self.git_files_frame.winfo_children():
            widget.destroy()
        self.git_file_checkboxes = []

        if not data["is_repo"]:
            self.git_branch_label.configure(text="Branch: N/A (non è un repository git)")
            self.git_graph_canvas.delete("all")
            self.git_graph_canvas.create_text(200, 50, text="Nessun repository Git trovato in questa cartella.", fill="white")
            return

        self.git_branch_label.configure(text=f"Branch: {data['branch']}")

        status_files = data["status_files"]
        if not status_files:
            label = ctk.CTkLabel(self.git_files_frame, text="Nessun file modificato. Working tree pulito.")
            label.pack(pady=5)
        else:
            for file_info in status_files:
                frame = ctk.CTkFrame(self.git_files_frame)
                frame.pack(pady=2, padx=5, fill="x")

                checkbox = ctk.CTkCheckBox(frame, text="", width=20)
                checkbox.pack(side="left", padx=5)
                self.git_file_checkboxes.append((checkbox, file_info['path']))

                # Visualizza lo stato
                staged_text = f"Staged: {file_info['staged']}" if file_info['staged'] != 'none' else ""
                unstaged_text = f"Unstaged: {file_info['unstaged']}" if file_info['unstaged'] != 'none' else ""
                status_text = ", ".join(filter(None, [staged_text, unstaged_text]))

                info = ctk.CTkLabel(frame, text=f"{file_info['path']} ({status_text})", anchor="w")
                info.pack(side="left", fill="x", expand=True)

        # Draw commit graph
        self.draw_commit_graph(data["commits"], data["nodes_map"])

        # Abilita i pulsanti se non ci sono operazioni in corso
        if not any(self.git_op_manager.is_operation_active(op) for op in ["checkout", "commit", "push", "merge", "revert", "resume", "stage", "unstage"]):
            self._set_git_buttons_state("normal")
        else:
            self._set_git_buttons_state("disabled")

    def start_git_auto_refresh(self):
        """Start automatic refresh of git status every 30 seconds."""
        self.after(30000, self.auto_refresh_git_status)

    def auto_refresh_git_status(self):
        """Auto-refresh git status if git tab is active."""
        # Check if git tab is the current tab and no operations are active
        if self.tabview.get() == "Git Status" and not self.git_op_manager.active_operations:
            self.refresh_git_status_async()
        # Schedule next refresh
        self.after(30000, self.auto_refresh_git_status)


    def draw_commit_graph(self, commits: List[Dict], nodes_map: Dict):
        """Draw commit graph on canvas based on pre-calculated layout data."""
        self.git_graph_canvas.delete("all")
        if not commits:
            self.git_graph_canvas.create_text(200, 50, text="Nessun commit trovato.", fill="white")
            return

        # Colori per i diversi branch/lane
        lane_colors = ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ac"]

        # Disegna le linee di connessione ai parent
        for commit in commits:
            for parent_hash in commit['parents']:
                if parent_hash in nodes_map:
                    parent_node = nodes_map[parent_hash]
                    self.git_graph_canvas.create_line(
                        commit['x'], commit['y'],
                        parent_node['x'], parent_node['y'],
                        fill=lane_colors[parent_node.get('x', 0) // 40 % len(lane_colors)],
                        width=2
                    )

        # Disegna i nodi dei commit
        for commit in commits:
            x, y = commit['x'], commit['y']
            col_index = (x - 30) // 40
            color = lane_colors[col_index % len(lane_colors)]

            # Crea un tag univoco per ogni commit
            commit_tag = f"commit_{commit['hash']}"

            # Disegna il cerchio del commit
            self.git_graph_canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill=color, outline="white", width=2, tags=commit_tag)

            # Aggiungi testo (hash e messaggio)
            # Troncamento del messaggio per una UI più pulita
            msg = commit['msg']
            display_msg = (msg[:45] + '...') if len(msg) > 45 else msg

            self.git_graph_canvas.create_text(x + 15, y, anchor="w", text=f"{commit['hash'][:7]} - {display_msg}", fill="white", tags=commit_tag)

            # Rendi il commit cliccabile
            self.git_graph_canvas.tag_bind(commit_tag, "<Button-1>", lambda e, c=commit: self.on_commit_click(c))

        # Aggiorna la scrollregion in modo robusto
        self.git_graph_canvas.update_idletasks()
        bbox = self.git_graph_canvas.bbox("all")
        if bbox:
            # Aggiungi padding per non tagliare il testo
            self.git_graph_canvas.configure(scrollregion=(bbox[0]-20, bbox[1]-20, bbox[2]+300, bbox[3]+20))

    def on_commit_click(self, commit: Dict):
        """Handle commit click with a context menu."""
        menu = tk.Menu(self, tearoff=0)
        commit_hash = commit['hash']
        short_hash = commit_hash[:7]

        menu.add_command(label=f"Checkout a {short_hash}", command=lambda: self.git_checkout_commit(commit_hash))
        menu.add_command(label=f"Crea branch da {short_hash}", command=lambda: self.git_create_branch_from(commit_hash))
        menu.add_command(label=f"Cherry-pick {short_hash}", command=lambda: self.git_cherry_pick_commit(commit_hash))
        menu.add_separator()
        menu.add_command(label="Copia Hash completo", command=lambda: self.copy_to_clipboard(commit_hash))
        menu.add_command(label="Mostra Dettagli", command=lambda: messagebox.showinfo(
            f"Commit {short_hash}",
            f"Hash: {commit['hash']}\nAutore: {commit['author']}\n\nMessaggio:\n{commit['msg']}"
        ))

        menu.post(self.winfo_pointerx(), self.winfo_pointery())

    def git_checkout_commit(self, commit_hash):
        """Checkout to a specific commit asynchronously."""
        self.git_op_manager.execute_async("checkout", self.git_manager.checkout, commit_hash)



    def git_commit(self):
        """Commit staged files asynchronously."""
        staged_files = [fi for fi in self.git_manager.get_status() if fi['staged'] != 'none']
        if not staged_files:
            messagebox.showinfo("Info", "Nessun file staged. Seleziona e stage i file da committare.")
            return

        msg = simpledialog.askstring("Commit", "Messaggio di commit:")
        if msg:
            self.git_op_manager.execute_async("commit", self.git_manager.commit, msg)

    def git_push(self):
        """Push commits asynchronously."""
        self.git_op_manager.execute_async("push", self.git_manager.push)

    def git_merge(self):
        """Merge a branch asynchronously."""
        branch = simpledialog.askstring("Merge", "Inserisci il nome del branch da mergiare:")
        if branch:
            self.git_op_manager.execute_async("merge", self.git_manager.merge, branch)

    def git_revert(self):
        """Revert a commit asynchronously."""
        commit_hash = simpledialog.askstring("Revert", "Inserisci l'hash del commit da annullare:")
        if commit_hash:
            self.git_op_manager.execute_async("revert", self.git_manager.revert_commit, commit_hash)

    def git_resume(self):
        """Resume a git operation asynchronously."""
        self.git_op_manager.execute_async("resume", self.git_manager.resume_operation)

    def stage_selected_files(self):
        """Stage selected files asynchronously."""
        selected = [fp for cb, fp in self.git_file_checkboxes if cb.get()]
        if not selected:
            messagebox.showinfo("Info", "Nessun file selezionato")
            return

        self.git_op_manager.execute_async("stage", self.git_manager.stage, selected)

    def unstage_selected_files(self):
        """Unstage selected files asynchronously."""
        selected = [fp for cb, fp in self.git_file_checkboxes if cb.get()]
        if not selected:
            messagebox.showinfo("Info", "Nessun file selezionato")
            return

        self.git_op_manager.execute_async("unstage", self.git_manager.unstage, selected)

    def git_create_branch_from(self, commit_hash: str):
        """Crea un nuovo branch da un commit specifico (asincrono)."""
        branch_name = simpledialog.askstring("Crea Branch", "Inserisci il nome del nuovo branch:")
        if not branch_name:
            return

        self.git_op_manager.execute_async("create_branch", self.git_manager.create_branch, branch_name, commit_hash)

    def git_cherry_pick_commit(self, commit_hash: str):
        """Esegue un cherry-pick di un commit (asincrono)."""
        if not messagebox.askyesno("Conferma Cherry-Pick", f"Sei sicuro di voler fare il cherry-pick del commit {commit_hash[:7]} sul branch corrente?"):
            return

        self.git_op_manager.execute_async("cherry_pick", self.git_manager.cherry_pick, commit_hash)

    # Assicurati di avere anche una funzione per la clipboard
    def copy_to_clipboard(self, text: str):
        """Pulisce la clipboard e copia il nuovo testo."""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update() # Necessario su alcuni sistemi

    # ==================== GESTIONE OPERAZIONI GIT ASINCRONE ====================

    def on_git_operation_started(self, operation_name: str):
        """Callback chiamato quando un'operazione Git inizia."""
        # Disabilita tutti i pulsanti Git
        self._set_git_buttons_state("disabled")

        if operation_name == "refresh":
            # Refresh speciale: solo indicatore leggero, no barra progresso completa
            self.git_status_label.configure(text="Aggiornamento in corso...")
            self.git_cancel_btn.configure(state="disabled")  # No cancellazione per refresh
        else:
            # Mostra progresso completo
            self.git_progress_bar.set(0.1)  # Inizio progresso
            self.git_status_label.configure(text=f"Operazione '{operation_name}' in corso...")
            self.git_cancel_btn.configure(state="normal")

        # Log
        log_queue.put(f"[GIT] Avviata operazione: {operation_name}\n")

    def on_git_operation_completed(self, operation_name: str, result):
        """Callback chiamato quando un'operazione Git è completata."""
        if operation_name == "refresh":
            # I dati sono stati caricati in background, ora disegna la UI
            self.refresh_git_status(result)
            self.after(1000, lambda: self._reset_git_ui_state())
            return

        # Gestisci il caso speciale di resume che restituisce 3 valori
        if operation_name == "resume" and len(result) == 3:
            success, message, op = result
            op_name = f"Ripresa {op}"
        else:
            success, message = result
            op_name = operation_name

        # Completa progresso
        self.git_progress_bar.set(1.0)

        if success:
            self.git_status_label.configure(text=f"✓ {op_name} completato", text_color="green")
            log_queue.put(f"[GIT] Operazione '{op_name}' completata con successo\n")
            # Aggiorna status Git dopo un breve delay
            self.after(500, self.refresh_git_status_async)
        else:
            self.git_status_label.configure(text=f"✗ {op_name} fallito", text_color="red")
            log_queue.put(f"[GIT ERROR] {op_name} fallito: {message}\n")
            messagebox.showerror(f"Errore {op_name}", message)

        # Riabilita pulsanti dopo un delay
        self.after(2000, lambda: self._reset_git_ui_state())

    def on_git_operation_error(self, operation_name: str, error_msg: str):
        """Callback chiamato quando un'operazione Git genera un errore."""
        self.git_progress_bar.set(0)
        self.git_status_label.configure(text=f"✗ Errore in {operation_name}", text_color="red")
        log_queue.put(f"[GIT ERROR] {operation_name} errore: {error_msg}\n")
        messagebox.showerror(f"Errore {operation_name}", error_msg)

        self.after(2000, lambda: self._reset_git_ui_state())

    def on_git_operation_cancel_requested(self, operation_name: str):
        """Callback chiamato quando la cancellazione è stata richiesta."""
        self.git_status_label.configure(text=f"Annullamento di '{operation_name}' richiesto...", text_color="orange")
        self.git_cancel_btn.configure(state="disabled")
        log_queue.put(f"[GIT] Richiesta di annullamento per '{operation_name}'. L'operazione terminerà a breve.\n")
        # La UI si resetterà quando il worker thread terminerà e chiamerà la callback appropriata

    def on_git_operation_cancelled(self, operation_name: str):
        """Callback chiamato quando un'operazione è terminata dopo una richiesta di annullamento."""
        self.git_status_label.configure(text=f"✓ Operazione '{operation_name}' terminata e annullata.", text_color="orange")
        log_queue.put(f"[GIT] Operazione '{operation_name}' terminata dopo richiesta di annullamento.\n")
        self.after(2000, self._reset_git_ui_state)

    def cancel_git_operation(self):
        """Annulla l'operazione Git corrente in modo robusto."""
        # Usa il manager per ottenere le operazioni attive invece di lista hardcoded
        active_operations = list(self.git_op_manager.active_operations)

        if not active_operations:
            # Nessuna operazione attiva
            return

        if len(active_operations) > 1:
            # Multiple operazioni attive (non dovrebbe accadere, ma gestisci)
            log_queue.put(f"[GIT WARNING] Multiple operazioni attive: {active_operations}\n")

        # Cancella la prima operazione attiva
        operation_to_cancel = active_operations[0]
        self.git_op_manager.cancel_operation(operation_to_cancel)

    def _set_git_buttons_state(self, state: str):
        """Imposta lo stato di tutti i pulsanti Git."""
        buttons = [
            self.commit_btn, self.push_btn, self.merge_btn, self.revert_btn, self.resume_btn,
            self.stage_selected_btn, self.unstage_selected_btn
        ]
        for btn in buttons:
            btn.configure(state=state)

    def _reset_git_ui_state(self):
        """Resetta l'interfaccia utente Git e aggiorna lo stato dei pulsanti in base al contesto."""
        self.git_progress_bar.set(0)
        self.git_status_label.configure(text="", text_color="white")
        self.git_cancel_btn.configure(state="disabled")

        if self.git_manager.is_git_repo():
            self._set_git_buttons_state("normal")

            # Logica di abilitazione dinamica
            _, _, op = self.git_manager.resume_operation()
            if not op:
                self.resume_btn.configure(state="disabled")

            staged_files = [fi for fi in self.git_manager.get_status() if fi['staged'] != 'none']
            if not staged_files:
                self.commit_btn.configure(state="disabled")
        else:
            self._set_git_buttons_state("disabled")


def main():
    """Main entry point."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
