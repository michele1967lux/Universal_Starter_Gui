# Manuale d'Uso - Universal Starter GUI

## Indice
1. [Introduzione](#introduzione)
2. [Requisiti di Sistema](#requisiti-di-sistema)
3. [Installazione](#installazione)
4. [Avvio dell'Applicazione](#avvio-dellapplicazione)
5. [Interfaccia Principale](#interfaccia-principale)
6. [Gestione degli Ambienti](#gestione-degli-ambienti)
7. [Gestione dei File](#gestione-dei-file)
8. [Configurazione e Salvataggio](#configurazione-e-salvataggio)
9. [Risoluzione dei Problemi](#risoluzione-dei-problemi)
10. [Domande Frequenti (FAQ)](#domande-frequenti-faq)

---

## Introduzione

**Universal Starter GUI** è un'applicazione desktop moderna che permette di:
- Avviare e gestire file eseguibili e script Python
- Creare e gestire ambienti virtuali Python (Venv e Conda)
- Monitorare lo stato dei processi in esecuzione con indicatori visivi
- Salvare e caricare configurazioni personalizzate

L'applicazione è ideale per sviluppatori che lavorano con più progetti Python e necessitano di gestire diversi ambienti virtuali e script contemporaneamente.

---

## Requisiti di Sistema

### Requisiti Minimi
- **Sistema Operativo**: Windows 10/11, Linux, macOS
- **Python**: Versione 3.9 o superiore
- **RAM**: Minimo 2 GB
- **Spazio su disco**: 100 MB per l'applicazione + spazio per ambienti virtuali

### Dipendenze Python
- `customtkinter` >= 5.2.0

### Opzionali
- **Conda/Miniconda/Anaconda**: Per la gestione di ambienti Conda

---

## Installazione

### Passo 1: Installare Python
Assicurarsi di avere Python 3.9 o superiore installato sul sistema.

Verificare l'installazione:
```bash
python --version
```

### Passo 2: Scaricare l'Applicazione
Clonare o scaricare il repository:
```bash
git clone https://github.com/mk4-67/UNIVERSAL-STARTER-GUI.git
cd UNIVERSAL-STARTER-GUI
```

### Passo 3: Installare le Dipendenze
Installare le librerie richieste:
```bash
pip install -r requirements.txt
```

### Passo 4: (Opzionale) Installare Conda
Se si desidera utilizzare ambienti Conda, installare Miniconda o Anaconda:
- **Miniconda**: https://docs.conda.io/en/latest/miniconda.html
- **Anaconda**: https://www.anaconda.com/download

---

## Avvio dell'Applicazione

Per avviare l'applicazione, eseguire:

```bash
python universal_starter.py
```

Oppure, su Linux/macOS:
```bash
./universal_starter.py
```

---

## Interfaccia Principale

L'interfaccia principale è divisa in tre sezioni:

### 1. Sezione Ambiente
- **Ambiente Attivo**: Mostra l'ambiente Python attualmente selezionato
- **Pulsante "Gestisci Ambienti"**: Apre la finestra di gestione ambienti

### 2. Sezione File
- **Lista File**: Mostra tutti i file aggiunti con indicatori di stato
- **Pulsante "Aggiungi File"**: Permette di aggiungere nuovi file alla lista

### 3. Sezione Controlli
- **Avvia Tutti**: Avvia tutti i file nella lista
- **Ferma Tutti**: Ferma tutti i processi in esecuzione
- **Salva Configurazione**: Salva la configurazione corrente

### Indicatori di Stato
- 🟢 **Verde**: Processo in esecuzione
- ⚫ **Grigio**: Processo non avviato
- 🔴 **Rosso**: Errore durante l'esecuzione

---

## Gestione degli Ambienti

### Aprire la Gestione Ambienti
Cliccare sul pulsante **"Gestisci Ambienti"** nella finestra principale.

### Tab Venv

#### Visualizzare Ambienti Venv Esistenti
La lista mostra tutti gli ambienti Venv nella cartella `.venvs`:
- **Nome**: Nome dell'ambiente
- **Percorso**: Percorso completo dell'ambiente

#### Creare un Nuovo Ambiente Venv
1. Inserire il nome desiderato nel campo "Nome"
2. Cliccare sul pulsante **"Crea"**
3. Attendere il completamento (l'output apparirà nella console)

#### Selezionare un Ambiente Venv
Cliccare sul pulsante **"Seleziona"** accanto all'ambiente desiderato.

#### Eliminare un Ambiente Venv
Cliccare sul pulsante **"Elimina"** (rosso) accanto all'ambiente da rimuovere.

**⚠️ Attenzione**: L'eliminazione è permanente e non può essere annullata.

### Tab Conda

#### Visualizzare Ambienti Conda Esistenti
La lista mostra tutti gli ambienti Conda installati sul sistema.

**Nota**: L'ambiente "base" non viene mostrato per evitare modifiche accidentali.

#### Creare un Nuovo Ambiente Conda
1. Inserire il nome desiderato nel campo "Nome"
2. Selezionare la versione di Python dal menu a tendina
3. Cliccare sul pulsante **"Crea"**
4. Attendere il completamento (il processo può richiedere alcuni minuti)

#### Selezionare un Ambiente Conda
Cliccare sul pulsante **"Seleziona"** accanto all'ambiente desiderato.

#### Eliminare un Ambiente Conda
Cliccare sul pulsante **"Elimina"** (rosso) accanto all'ambiente da rimuovere.

**⚠️ Attenzione**: L'eliminazione è permanente e non può essere annullata.

### Console Output
La console nella parte inferiore di ogni tab mostra:
- Messaggi di progresso durante la creazione/eliminazione
- Eventuali errori o warning
- Conferme di operazioni completate con successo

---

## Gestione dei File

### Aggiungere un File
1. Cliccare sul pulsante **"➕ Aggiungi File"**
2. Selezionare il file dal browser (script Python, eseguibili, ecc.)
3. Il file apparirà nella lista con il suo nome e percorso

### Avviare un File
- **Singolo file**: Cliccare sul pulsante **▶** accanto al file
- **Tutti i file**: Cliccare su **"▶ Avvia Tutti"** nella sezione controlli

### Fermare un File
- **Singolo file**: Cliccare sul pulsante **⏹** accanto al file
- **Tutti i file**: Cliccare su **"⏹ Ferma Tutti"** nella sezione controlli

### Rimuovere un File
Cliccare sul pulsante **🗑** (cestino) accanto al file da rimuovere.

**Nota**: Il file verrà rimosso solo dalla lista, non dal disco.

### Comportamento con Ambienti
- **Con Venv**: Il file viene eseguito usando il Python dell'ambiente Venv selezionato
- **Con Conda**: Il file viene eseguito usando `conda run` con l'ambiente selezionato
- **Senza ambiente**: Il file viene eseguito con il Python di sistema

---

## Configurazione e Salvataggio

### File di Configurazione
L'applicazione salva automaticamente la configurazione nel file `config.json`.

#### Struttura del File
```json
{
  "environment": {
    "type": "venv",
    "name": "mio_ambiente",
    "path": "/path/to/.venvs/mio_ambiente"
  },
  "files": [
    {
      "name": "script.py",
      "path": "/path/to/script.py"
    }
  ]
}
```

### Salvataggio Automatico
La configurazione viene salvata automaticamente quando:
- Si aggiunge o rimuove un file
- Si seleziona un nuovo ambiente
- Si clicca sul pulsante **"💾 Salva Configurazione"**

### Caricamento Automatico
Al riavvio dell'applicazione, la configurazione viene caricata automaticamente dal file `config.json`.

---

## Risoluzione dei Problemi

### Problema: "Conda non trovato"

**Sintomi**: Errore durante la creazione di ambienti Conda o lista vuota.

**Soluzione**:
1. Verificare che Conda sia installato:
   ```bash
   conda --version
   ```
2. Se non installato, scaricare Miniconda o Anaconda
3. Assicurarsi che Conda sia nel PATH di sistema

### Problema: "Ambiente Venv non si crea"

**Sintomi**: Errore durante la creazione di un ambiente Venv.

**Soluzione**:
1. Verificare che Python sia correttamente installato
2. Verificare i permessi di scrittura nella cartella `.venvs`
3. Provare a creare l'ambiente manualmente:
   ```bash
   python -m venv .venvs/test_env
   ```

### Problema: "Script non si avvia"

**Sintomi**: L'indicatore diventa rosso immediatamente.

**Soluzione**:
1. Verificare che il percorso dello script sia corretto
2. Verificare che l'ambiente selezionato contenga tutte le dipendenze necessarie
3. Controllare che lo script sia eseguibile (Linux/macOS)
4. Verificare eventuali errori di sintassi nello script

### Problema: "L'applicazione si chiude improvvisamente"

**Sintomi**: L'applicazione si chiude senza messaggi di errore.

**Soluzione**:
1. Avviare l'applicazione da terminale per vedere eventuali errori:
   ```bash
   python universal_starter.py
   ```
2. Verificare che customtkinter sia installato correttamente:
   ```bash
   pip install --upgrade customtkinter
   ```

### Problema: "Processo non si ferma"

**Sintomi**: Cliccare su "Ferma" non termina il processo.

**Soluzione**:
1. Attendere qualche secondo (timeout di 5 secondi)
2. Il processo verrà forzatamente terminato se non risponde
3. In alternativa, terminare manualmente dal task manager

---

## Domande Frequenti (FAQ)

### D: Posso usare l'applicazione senza Conda?
**R**: Sì, è possibile usare solo ambienti Venv. Conda è completamente opzionale.

### D: Dove vengono salvati gli ambienti Venv?
**R**: Gli ambienti Venv vengono salvati nella cartella `.venvs` nella directory dell'applicazione.

### D: Posso aggiungere file non-Python?
**R**: Sì, è possibile aggiungere qualsiasi file eseguibile. Per file non-Python, l'applicazione tenterà di eseguirli direttamente.

### D: È possibile eseguire script su ambienti remoti?
**R**: No, l'applicazione supporta solo ambienti locali (Venv e Conda locali).

### D: Quanti file posso gestire contemporaneamente?
**R**: Non c'è un limite tecnico, ma si consiglia di non superare i 10-15 processi per evitare problemi di performance.

### D: L'applicazione supporta Docker?
**R**: No, attualmente Docker non è supportato. L'applicazione gestisce solo ambienti Python Venv e Conda.

### D: Come posso contribuire al progetto?
**R**: Il progetto è open source. È possibile contribuire tramite pull request sul repository GitHub.

### D: È possibile personalizzare l'interfaccia?
**R**: L'applicazione usa customtkinter con tema scuro. È possibile modificare il codice per personalizzare l'aspetto.

### D: Come posso vedere l'output degli script in esecuzione?
**R**: Attualmente l'output non viene mostrato nell'interfaccia. È possibile reindirizzare l'output a file di log modificando gli script.

### D: L'applicazione funziona su Raspberry Pi?
**R**: Sì, se Python 3.9+ e le dipendenze sono installate. Le prestazioni dipendono dal modello.

---

## Supporto e Contatti

Per segnalare bug, richiedere funzionalità o ottenere supporto:
- **GitHub Issues**: https://github.com/mk4-67/UNIVERSAL-STARTER-GUI/issues
- **Repository**: https://github.com/mk4-67/UNIVERSAL-STARTER-GUI

---

## Licenza

Questo progetto è distribuito sotto licenza MIT. Vedere il file LICENSE per i dettagli.

---

## Crediti

Sviluppato utilizzando:
- **Python**: Linguaggio di programmazione
- **CustomTkinter**: Framework per l'interfaccia grafica
- **subprocess**: Gestione processi
- **threading**: Esecuzione asincrona

---

**Versione Manuale**: 1.0  
**Data**: 2025-10-18  
**Autore**: mk4-67
