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
        # Crea tabview principale
        self.tabview = ctk.CTkTabview(self, width=1200, height=700)
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
        self.git_branch_label.pack(side="left")
        refresh_git_btn = ctk.CTkButton(git_header, text="Aggiorna", command=self.refresh_git_status)
        refresh_git_btn.pack(side="right")

        # Scrollable frame per file git
        self.git_files_frame = ctk.CTkScrollableFrame(git_tab)
        self.git_files_frame.pack(fill="both", expand=True, padx=10, pady=10)

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
        self.git_graph_canvas = ctk.CTkCanvas(canvas_frame, bg="gray20")
        scrollbar = ctk.CTkScrollbar(canvas_frame, command=self.git_graph_canvas.yview)
        self.git_graph_canvas.configure(yscrollcommand=scrollbar.set)
        self.git_graph_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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

        # Aggiungi tooltip
        self.create_tooltip(self.commit_btn, "Crea un nuovo commit con i file attualmente staged.")
        self.create_tooltip(self.push_btn, "Invia i commit locali al repository remoto.")
        self.create_tooltip(self.merge_btn, "Unisci un branch selezionato nel branch corrente.")
        self.create_tooltip(self.revert_btn, "Annulla le modifiche di un commit specifico.")
        self.create_tooltip(self.resume_btn, "Riprendi un'operazione interrotta (merge/rebase).")
        self.create_tooltip(self.stage_selected_btn, "Aggiungi i file selezionati all'area di staging.")
        self.create_tooltip(self.unstage_selected_btn, "Rimuovi i file selezionati dall'area di staging.")

        # Inizializza status git
        self.refresh_git_status()

        # Start auto-refresh for git status
        self.start_git_auto_refresh()

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

    def refresh_git_status(self):
        """Refresh the git status display."""
        # Clear existing widgets
        for widget in self.git_files_frame.winfo_children():
            widget.destroy()
        self.git_file_checkboxes = []

        # Get current branch
        try:
            result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=os.getcwd())
            print(f"Git branch result: {result.returncode}, stdout: '{result.stdout.strip()}', stderr: '{result.stderr.strip()}'")
            if result.returncode == 0:
                branch = result.stdout.strip()
                self.git_branch_label.configure(text=f"Branch: {branch}")
            else:
                self.git_branch_label.configure(text="Branch: N/A (non git repo)")
        except FileNotFoundError:
            self.git_branch_label.configure(text="Branch: N/A (git non trovato)")

        # Get git status
        try:
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines == ['']:
                    # No changes
                    label = ctk.CTkLabel(self.git_files_frame, text="Nessun file modificato")
                    label.pack(pady=5)
                else:
                    for line in lines:
                        if line:
                            status = line[:2]
                            file_path = line[3:]
                            # Determine color and text
                            if status[0] in ['M', 'A', 'D', 'R'] or status[1] in ['M', 'A', 'D', 'R']:
                                color = "green" if status[0] != ' ' else "red"
                                status_text = "Staged" if status[0] != ' ' else "Modified"
                            elif status[0] == '?':
                                color = "yellow"
                                status_text = "Untracked"
                            else:
                                color = "gray"
                                status_text = "Ignored"

                            frame = ctk.CTkFrame(self.git_files_frame)
                            frame.pack(pady=2, padx=5, fill="x")
                            # Checkbox for staging
                            checkbox = ctk.CTkCheckBox(frame, text="", width=20)
                            checkbox.pack(side="left", padx=5)
                            self.git_file_checkboxes.append((checkbox, file_path, status))
                            indicator = ctk.CTkLabel(frame, text="●", text_color=color, font=("Arial", 20))
                            indicator.pack(side="left", padx=5)
                            info = ctk.CTkLabel(frame, text=f"{file_path} ({status_text})", anchor="w")
                            info.pack(side="left", fill="x", expand=True)
            else:
                label = ctk.CTkLabel(self.git_files_frame, text="Errore nel recupero status git")
                label.pack(pady=5)
        except FileNotFoundError:
            label = ctk.CTkLabel(self.git_files_frame, text="Git non installato")
            label.pack(pady=5)

        # Check if repo has commits
        has_commits = False
        try:
            count_result = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True, cwd=os.getcwd())
            if count_result.returncode == 0 and int(count_result.stdout.strip()) > 0:
                has_commits = True
            print(f"Has commits: {has_commits}, count: {count_result.stdout.strip()}")
        except (FileNotFoundError, ValueError) as e:
            print(f"Error checking commits: {e}")
            pass

        # Draw branch graph
        if has_commits:
            commits = self.parse_git_log()
            self.draw_commit_graph(commits)
        else:
            self.git_graph_canvas.delete("all")
            self.git_graph_canvas.create_text(100, 100, text="Nessun commit trovato nel repository", fill="white")

        # Abilita pulsanti se git disponibile
        try:
            subprocess.run(["git", "status"], capture_output=True, cwd=os.getcwd())
            self.commit_btn.configure(state="normal")
            self.push_btn.configure(state="normal")
            self.merge_btn.configure(state="normal")
            self.revert_btn.configure(state="normal")
            self.resume_btn.configure(state="normal")
        except FileNotFoundError:
            self.commit_btn.configure(state="disabled")
            self.push_btn.configure(state="disabled")
            self.merge_btn.configure(state="disabled")
            self.revert_btn.configure(state="disabled")
            self.resume_btn.configure(state="disabled")

    def start_git_auto_refresh(self):
        """Start automatic refresh of git status every 30 seconds."""
        self.after(30000, self.auto_refresh_git_status)

    def auto_refresh_git_status(self):
        """Auto-refresh git status if git tab is active."""
        # Check if git tab is the current tab
        if self.tabview.get() == "Git Status":
            self.refresh_git_status()
        # Schedule next refresh
        self.after(30000, self.auto_refresh_git_status)

    def parse_git_log(self):
        """Parse git log for commit graph."""
        try:
            result = subprocess.run(["git", "log", "--pretty=format:%H|%s|%p", "--all", "-10"], capture_output=True, text=True, cwd=os.getcwd())
            print(f"Git log result: {result.returncode}, stdout: '{result.stdout[:100]}...', stderr: '{result.stderr}'")
            if result.returncode == 0:
                commits = []
                lines = result.stdout.strip().split('\n')
                y = 20
                for line in lines:
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            hash_short = parts[0][:7]
                            msg = parts[1][:20]
                            parents = parts[2:] if len(parts) > 2 else []
                            commits.append({'hash': parts[0], 'msg': msg, 'parents': parents, 'x': 50, 'y': y})
                            y += 70  # Increased spacing
                print(f"Parsed {len(commits)} commits")
                return commits
            else:
                print(f"Parse git log error: {result.stderr}")
                return []
        except Exception as e:
            print(f"Error parsing git log: {e}")
            return []

    def draw_commit_graph(self, commits):
        """Draw commit graph on canvas."""
        self.git_graph_canvas.delete("all")
        print(f"Drawing {len(commits)} commits")
        if not commits:
            self.git_graph_canvas.create_text(100, 100, text="Errore nel caricamento grafico", fill="white")
            return

        import textwrap
        max_y = 0
        for i, commit in enumerate(commits):
            x, y = commit['x'], commit['y']
            # Draw rectangle larger and lower
            self.git_graph_canvas.create_rectangle(x, y, x+200, y+50, fill="lightblue", outline="white")
            # Draw text: hash and wrapped message
            self.git_graph_canvas.create_text(x+100, y+10, text=commit['hash'][:7], fill="black", font=("Arial", 8, "bold"))
            wrapped_lines = textwrap.wrap(commit['msg'], width=25)
            for j, line in enumerate(wrapped_lines[:4]):  # Max 4 lines
                self.git_graph_canvas.create_text(x+100, y+25 + j*10, text=line, fill="black", font=("Arial", 8))
            # Bind click
            self.git_graph_canvas.tag_bind(f"commit_{i}", "<Button-1>", lambda e, c=commit: self.on_commit_click(c))
            self.git_graph_canvas.addtag_withtag(f"commit_{i}", self.git_graph_canvas.create_rectangle(x, y, x+200, y+50))
            # Draw lines to parents
            for parent_hash in commit['parents']:
                parent_index = next((j for j, c in enumerate(commits) if c['hash'] == parent_hash), None)
                if parent_index is not None:
                    parent_y = commits[parent_index]['y'] + 25
                    self.git_graph_canvas.create_line(x+100, y+50, commits[parent_index]['x']+100, parent_y, fill="white", arrow=tk.LAST)
            max_y = max(max_y, y + 50)

        # Update scroll region
        self.git_graph_canvas.configure(scrollregion=self.git_graph_canvas.bbox("all"))
        self.git_graph_canvas.update_idletasks()

    def on_commit_click(self, commit):
        """Handle commit click."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Checkout", command=lambda: self.git_checkout_commit(commit['hash']))
        menu.add_command(label="Revert", command=lambda: self.git_revert_commit(commit['hash']))
        menu.add_command(label="Show Details", command=lambda: messagebox.showinfo("Commit", f"Hash: {commit['hash']}\nMsg: {commit['msg']}"))
        menu.post(self.winfo_pointerx(), self.winfo_pointery())

    def git_checkout_commit(self, commit_hash):
        """Checkout to commit."""
        try:
            result = subprocess.run(["git", "checkout", commit_hash], cwd=os.getcwd(), capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Successo", f"Checkout a {commit_hash[:7]}")
                self.refresh_git_status()
            else:
                messagebox.showerror("Errore", result.stderr)
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def git_revert_commit(self, commit_hash):
        """Revert commit."""
        try:
            result = subprocess.run(["git", "revert", commit_hash], cwd=os.getcwd(), capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Successo", f"Revert di {commit_hash[:7]}")
                self.refresh_git_status()
            else:
                messagebox.showerror("Errore", result.stderr)
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def git_commit(self):
        # Check if there are staged files
        try:
            staged_result = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=os.getcwd(), capture_output=True, text=True)
            if staged_result.returncode != 0 or not staged_result.stdout.strip():
                messagebox.showinfo("Info", "Nessun file staged. Seleziona e stage i file da committare.")
                return
        except Exception as e:
            messagebox.showerror("Errore", f"Errore controllo staged: {e}")
            return

        msg = simpledialog.askstring("Commit", "Messaggio commit:")
        if msg:
            try:
                result = subprocess.run(["git", "commit", "-m", msg], cwd=os.getcwd(), capture_output=True, text=True)
                if result.returncode == 0:
                    messagebox.showinfo("Successo", "Commit effettuato")
                    self.refresh_git_status()
                else:
                    messagebox.showerror("Errore", result.stderr)
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def git_push(self):
        try:
            result = subprocess.run(["git", "push"], cwd=os.getcwd(), capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Successo", "Push effettuato")
                self.refresh_git_status()
            else:
                messagebox.showerror("Errore", result.stderr)
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def git_merge(self):
        branch = simpledialog.askstring("Merge", "Branch da mergiare:")
        if branch:
            try:
                result = subprocess.run(["git", "merge", branch], cwd=os.getcwd(), capture_output=True, text=True)
                if result.returncode == 0:
                    messagebox.showinfo("Successo", "Merge effettuato")
                    self.refresh_git_status()
                else:
                    messagebox.showerror("Errore", result.stderr)
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def git_revert(self):
        commit = simpledialog.askstring("Revert", "Commit da revertire:")
        if commit:
            try:
                result = subprocess.run(["git", "revert", commit], cwd=os.getcwd(), capture_output=True, text=True)
                if result.returncode == 0:
                    messagebox.showinfo("Successo", "Revert effettuato")
                    self.refresh_git_status()
                else:
                    messagebox.showerror("Errore", result.stderr)
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def git_resume(self):
        # Check if in merge
        if os.path.exists(".git/MERGE_HEAD"):
            cmd = ["git", "merge", "--continue"]
        elif os.path.exists(".git/rebase-apply"):
            cmd = ["git", "rebase", "--continue"]
        else:
            messagebox.showinfo("Info", "Nessuna operazione da riprendere")
            return
        try:
            result = subprocess.run(cmd, cwd=os.getcwd(), capture_output=True, text=True)
            if result.returncode == 0:
                messagebox.showinfo("Successo", "Operazione ripresa")
                self.refresh_git_status()
            else:
                messagebox.showerror("Errore", result.stderr)
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def stage_selected_files(self):
        """Stage selected files."""
        selected = [fp for cb, fp, st in self.git_file_checkboxes if cb.get()]
        if not selected:
            messagebox.showinfo("Info", "Nessun file selezionato")
            return
        for file_path in selected:
            try:
                subprocess.run(["git", "add", file_path], cwd=os.getcwd(), check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Errore", f"Errore staging {file_path}: {e}")
        self.refresh_git_status()

    def unstage_selected_files(self):
        """Unstage selected files."""
        selected = [fp for cb, fp, st in self.git_file_checkboxes if cb.get()]
        if not selected:
            messagebox.showinfo("Info", "Nessun file selezionato")
            return
        for file_path in selected:
            try:
                subprocess.run(["git", "reset", "HEAD", file_path], cwd=os.getcwd(), check=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Errore", f"Errore unstage {file_path}: {e}")
        self.refresh_git_status()


def main():
    """Main entry point."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
