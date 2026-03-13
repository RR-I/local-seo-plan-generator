# 📍 Local SEO Editorial Planner

Applicazione Streamlit per generare piani editoriali ottimizzati per Google Business Profile partendo da analisi SERP reali e contenuti estratti dal web o dal sito dell’attività. Pensata per marketer e agenzie Local SEO che desiderano creare post personalizzati e pronti all’uso in pochi minuti.

---

## 🚀 Funzionalità principali

- **Accesso protetto**: login con password tramite `st.secrets`.
- **Analisi SERP DataForSEO**: interrogazione delle SERP locali (fino a 5 risultati) su Google.
- **Content scraping**: estrazione e sintesi dei contenuti delle pagine migliori.
- **Generazione copy**: creazione automatica di post in formato JSON tramite OpenAI, ottimizzati per Google Business Profile.
- **Piano editoriale**: tabella con argomento, fonti analizzate, copy completo e colonne per immagini/date.
- **Esportazione**: download in CSV o Excel del piano generato.
- **Gestione cache**: pulizia guidata per forzare nuove analisi o modifiche di prompt.

---

## 🧱 Struttura del progetto

```
.
├── app.py                 # Codice principale Streamlit
├── requirements.txt       # Dipendenze Python
└── README.md              # Questo documento
```

> **Nota**: lo script richiede Python 3.9+.

---

## 🔧 Requisiti

- **Account DataForSEO** con credenziali API attive (SERP + On-Page).
- **Chiave API OpenAI** (modello `gpt-4.1` o superiore).
- **Streamlit** e librerie indicate in `requirements.txt`.
- **openpyxl** (opzionale) per l’esportazione diretta in Excel.

---

## 📦 Installazione

1. Clona il repository o copia i file dell’app:
   ```bash
   git clone https://github.com/<tuo-repo>/local-seo-editorial-planner.git
   cd local-seo-editorial-planner
   ```

2. Crea (opzionale ma consigliato) un ambiente virtuale:
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

4. (Facoltativo) per l’esportazione Excel:
   ```bash
   pip install openpyxl
   ```

---

## 🔐 Configurazione segreti

Lo script legge le credenziali da `st.secrets`. Crea un file `.streamlit/secrets.toml` nella root del progetto:

```toml
APP_PASSWORD = "password_di_accesso"

DATAFORSEO_LOGIN = "email_dataforseo"
DATAFORSEO_PASSWORD = "password_api_dataforseo"

OPENAI_API_KEY = "sk-..."
```

> **Sicurezza**: non committare il file dei segreti. Aggiungi `.streamlit/` al `.gitignore`.

---

## ▶️ Avvio dell’app

Esegui:

```bash
streamlit run app.py
```

Apri il browser all’indirizzo mostrato (di default `http://localhost:8501`), quindi inserisci la password impostata nei segreti.

---

## 🔄 Flusso di utilizzo

1. **Login** con password statica.
2. **Compila i dati** dell’attività: nome, settore, sito, località, tono, numero di post.
3. **Inserisci gli argomenti** (uno per riga) e un brief opzionale.
4. **Scegli la strategia**:
   - `Dal sito web (site:)` → ricerca limitata al dominio indicato.
   - `Dal web (query generica)` → SERP organica standard.
5. Avvia la generazione:
   - Analisi SERP
   - Estrazione contenuti principali
   - Sintesi + generazione post
6. Visualizza il piano editoriale e scarica CSV/Excel.

---

## 🛠️ Note tecniche

- **Cache**: `st.cache_resource` e `st.cache_data` ottimizzano chiamate API ripetute. Usa il pulsante “Svuota cache” per invalidarle.
- **Limiti API**:
  - SERP: massimo 5 risultati per query (`depth=5`).
  - Contenuti: truncazione a 4.000 caratteri per prompt.
- **Error handling**: il flusso prosegue anche se una pagina non restituisce contenuto; il post verrà generato sui testi disponibili.
- **OpenAI**: output richiesto esclusivamente in JSON; se non valido, viene effettuato fallback su parsing manuale dei post.

---

## 📄 Licenza

Specificare la licenza del progetto (ad es. MIT, proprietaria, ecc.). Se non definita, aggiungi una sezione dedicata.

---

## 🤝 Contributi

- Apri una issue per bug o feature request.
- Effettua un fork e invia pull request con descrizione dettagliata.

---

## 📬 Supporto

Per domande o assistenza, contatta il maintainer del progetto oppure apri una issue su GitHub.

Buon lavoro con i tuoi piani editoriali Local SEO! 🚀
