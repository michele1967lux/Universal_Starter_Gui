# Manuale d'Uso - Universal Starter GUI

> **📚 Nota**: Per una panoramica generale e istruzioni di installazione in italiano e inglese, consulta il [README.md](../README.md) principale.

> **💡 Suggerimento**: Se stai cercando una guida rapida, la sezione italiana nel README.md potrebbe essere sufficiente. Questo manuale fornisce istruzioni dettagliate e approfondite.

---

## Indice
1. [Introduzione](#introduzione)
2. [Requisiti di Sistema](#requisiti-di-sistema)
3. [Installazione](#installazione)
4. [Avvio dell'Applicazione](#avvio-dellapplicazione)
5. [Interfaccia Principale](#interfaccia-principale)
6. [Gestione degli Ambienti](#gestione-degli-ambienti)
7. [Gestione dei File](#gestione-dei-file)
8. [Integrazione Git](#integrazione-git)
9. [Configurazione e Salvataggio](#configurazione-e-salvataggio)
10. [Risoluzione dei Problemi](#risoluzione-dei-problemi)
11. [Domande Frequenti (FAQ)](#domande-frequenti-faq)

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

## Integrazione Git

### Panoramica

Universal Starter GUI include un client Git integrato completo che permette di gestire repository Git direttamente dall'interfaccia. Questa funzionalità è particolarmente utile per sviluppatori che lavorano su più progetti e vogliono mantenere il controllo di versione senza dover lasciare l'applicazione.

### Accesso alle Funzionalità Git

Per accedere alle funzionalità Git:
1. Clicca sulla tab **"Git Status"** nella finestra principale
2. Se la cartella corrente non è un repository Git, vedrai un pulsante per inizializzarne uno
3. Una volta in un repository valido, vedrai il grafico commit e i controlli Git

### Grafico Commit Visuale

Il grafico commit mostra la cronologia del repository in modo visuale:

- **Cerchi colorati**: Rappresentano singoli commit
- **Linee**: Mostrano le relazioni parent-child tra commit
- **Colonne**: Separano diversi branch per chiarezza visiva
- **Testo**: Mostra hash abbreviato del commit e messaggio

#### Interazione con i Commit

**Click Singolo**: Clicca su un commit per aprire un menu contestuale con azioni:
- **Checkout a [hash]**: Sposta HEAD a quel commit (stato detached)
- **Crea branch da [hash]**: Crea un nuovo branch da quel punto
- **Cherry-pick [hash]**: Applica le modifiche di quel commit sul branch corrente
- **Copia Hash completo**: Copia l'hash SHA completo negli appunti
- **Mostra Dettagli**: Visualizza informazioni dettagliate sul commit

### Gestione File e Staging

#### Visualizzazione Stato File

La sezione superiore della tab Git Status mostra tutti i file modificati:
- **Staged**: File pronti per essere committati (verde)
- **Unstaged**: File modificati ma non ancora staged (giallo)
- **Untracked**: File nuovi non tracciati da Git (rosso)

#### Operazioni di Staging

1. **Stage Selezionati**:
   - Seleziona i file usando le checkbox
   - Clicca "Stage Selezionati"
   - I file si sposteranno nell'area di staging

2. **Unstage Selezionati**:
   - Seleziona i file staged
   - Clicca "Unstage Selezionati"
   - I file verranno rimossi dall'area di staging

### Operazioni Git Principali

#### Commit

1. Assicurati di aver staged i file desiderati
2. Clicca sul pulsante **"Commit"**
3. Inserisci un messaggio di commit descrittivo
4. Conferma per creare il commit

**Suggerimento**: Scrivi messaggi di commit chiari che descrivano cosa è stato cambiato e perché.

#### Push

1. Assicurati di aver committato le tue modifiche
2. Clicca sul pulsante **"Push"**
3. I commit locali verranno inviati al repository remoto
4. Vedrai un messaggio di conferma o errore

#### Merge

1. Clicca sul pulsante **"Merge"**
2. Inserisci il nome del branch da mergiare nel branch corrente
3. Conferma l'operazione
4. Se ci sono conflitti, dovrai risolverli manualmente

#### Crea Branch

**Dal pulsante principale**:
1. Clicca **"Crea Branch"**
2. Inserisci il nome del nuovo branch
3. Il branch verrà creato dal punto corrente (HEAD)

**Dal menu contestuale commit**:
1. Click destro su un commit specifico
2. Seleziona "Crea branch da [hash]"
3. Inserisci il nome del branch
4. Il branch verrà creato da quel commit

#### Revert

1. Clicca sul pulsante **"Revert"**
2. Inserisci l'hash del commit da annullare
3. Conferma l'operazione
4. Verrà creato un nuovo commit che annulla le modifiche

**Nota**: Revert non modifica la cronologia, ma crea un nuovo commit.

#### Resume

Se un'operazione (merge/rebase) è stata interrotta:
1. Risolvi i conflitti manualmente
2. Clicca **"Resume"** per continuare l'operazione
3. L'operazione verrà completata

### Indicatori di Progresso

Durante le operazioni Git:
- **Barra di progresso**: Mostra lo stato dell'operazione
- **Testo di stato**: Descrive cosa sta accadendo
- **Pulsante Annulla**: Permette di cancellare operazioni lunghe (quando possibile)

### Operazioni Asincrone

Tutte le operazioni Git vengono eseguite in background:
- **Nessun blocco UI**: L'interfaccia rimane reattiva
- **Feedback visuale**: Indicatori di progresso chiari
- **Gestione errori**: Messaggi di errore informativi
- **Cancellazione**: Possibilità di annullare operazioni lunghe

### Limiti e Configurazione

#### Numero di Commit Visualizzati

- **Default**: 50 commit
- **Configurazione**: Modifica il valore nel campo "Commit da mostrare"
- **Aggiorna**: Clicca "Aggiorna" per ricaricare con il nuovo limite

#### Limitazioni

- Le operazioni Git richiedono che Git sia installato e nel PATH
- Alcuni comandi potrebbero richiedere privilegi amministratore
- Le operazioni su repository molto grandi potrebbero richiedere tempo
- Non tutte le funzionalità Git avanzate sono supportate dall'interfaccia

### Risoluzione Problemi Git

#### "Git non trovato"

**Soluzione**:
1. Verifica che Git sia installato: `git --version`
2. Aggiungi Git al PATH di sistema
3. Riavvia l'applicazione

#### "Non è un repository Git"

**Soluzione**:
1. Naviga in una cartella che contiene un repository Git
2. Oppure usa il pulsante "Inizializza Repository Qui"

#### "Conflitti durante il merge"

**Soluzione**:
1. Risolvi i conflitti manualmente nei file
2. Stage i file risolti
3. Usa il pulsante "Resume" per completare il merge

#### "Push rifiutato"

**Possibili cause**:
- Branch remoto ha commit che non hai localmente
- Autenticazione fallita
- Permessi insufficienti

**Soluzione**:
1. Esegui pull per sincronizzare
2. Verifica le credenziali di autenticazione
3. Controlla i permessi sul repository remoto

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

### D: Posso usare Git senza interfaccia grafica?
**R**: Sì, puoi continuare a usare Git dalla riga di comando. L'integrazione Git nell'app è opzionale e lavora sullo stesso repository.

### D: Cosa succede se cancello l'ambiente Conda base?
**R**: L'ambiente "base" non viene mostrato nella lista per prevenire eliminazioni accidentali. Non è possibile eliminarlo dall'app.

### D: Posso usare l'app per progetti non-Python?
**R**: L'app è ottimizzata per Python, ma puoi aggiungere qualsiasi script eseguibile. Le funzionalità di ambiente sono specifiche per Python.

### D: Come contribuisco al progetto?
**R**: Vedi [CONTRIBUTING.md](../CONTRIBUTING.md) per linee guida dettagliate. Accogliamo contributi di codice, documentazione e traduzioni!

---

## Supporto e Contatti

Per segnalare bug, richiedere funzionalità o ottenere supporto:
- **GitHub Issues**: [github.com/michele1967lux/Universal_Starter_Gui/issues](https://github.com/michele1967lux/Universal_Starter_Gui/issues)
- **Repository**: [github.com/michele1967lux/Universal_Starter_Gui](https://github.com/michele1967lux/Universal_Starter_Gui)
- **Discussioni**: Usa le GitHub Discussions per domande generali

### Come Supportare il Progetto

Se trovi utile questo progetto, considera di:
- ⭐ **Mettere una stella** al repository su GitHub
- 🐛 **Segnalare bug** per migliorare la qualità
- 💡 **Suggerire nuove funzionalità**
- 🔧 **Contribuire** con codice o documentazione
- 📖 **Migliorare la documentazione**
- 🌍 **Tradurre** in altre lingue

---

## Licenza

Questo progetto è distribuito sotto **licenza MIT**. Vedere il file [LICENSE](../LICENSE) per i dettagli.

La licenza MIT permette:
- ✅ Uso commerciale
- ✅ Modifica del codice
- ✅ Distribuzione
- ✅ Uso privato

---

## Crediti

**Sviluppatore Principale**: [michele1967lux](https://github.com/michele1967lux)

Sviluppato utilizzando:
- **Python**: Linguaggio di programmazione principale
- **CustomTkinter**: Framework per l'interfaccia grafica moderna
- **psutil**: Gestione processi e sistema
- **subprocess**: Esecuzione processi
- **threading**: Esecuzione asincrona

### Ringraziamenti Speciali

- **Community CustomTkinter** per l'eccellente framework UI
- **Tutti i contributori** che migliorano il progetto
- **Gli utenti** che forniscono feedback prezioso

---

## Changelog

### Versione 1.2 (Ottobre 2025)
- ✨ Documentazione bilingue completa (Italiano/Inglese)
- ✨ Guida contributi (CONTRIBUTING.md)
- ✨ README professionale con call-to-action
- 📚 Manuale utente espanso con sezione Git
- 🔧 Migliorata documentazione codice
- 🌍 Struttura documentazione organizzata

### Versione 1.1 (Ottobre 2025)
- ✨ Integrazione Git completa con grafico visuale
- ✨ Gestione processi localhost
- ✨ Clonazione e rinominazione ambienti
- 🔧 Editor requirements.txt integrato
- 🔍 Test CUDA/PyTorch

### Versione 1.0 (Ottobre 2025)
- ✨ Release iniziale
- 🚀 Gestione script Python
- 🐍 Supporto ambienti Venv e Conda
- 💾 Configurazione persistente
- 🎨 Interfaccia CustomTkinter

---

<div align="center">

**Versione Manuale**: 1.2  
**Data Aggiornamento**: Ottobre 2025  
**Autore**: [michele1967lux](https://github.com/michele1967lux)

**Made with ❤️ for the Python community**

[![GitHub Stars](https://img.shields.io/github/stars/michele1967lux/Universal_Starter_Gui?style=social)](https://github.com/michele1967lux/Universal_Starter_Gui/stargazers)

**📚 Vedi anche**: [README.md](../README.md) | [CONTRIBUTING.md](../CONTRIBUTING.md)

</div>
