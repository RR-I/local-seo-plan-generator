import streamlit as st
import base64, json, requests, re
from typing import List
from openai import OpenAI
from io import BytesIO
import pandas as pd

# ============================
# CONFIGURAZIONE PAGINA
# ============================
st.set_page_config(
    page_title="Local SEO Editorial Planner",
    page_icon="📍",
    layout="wide"
)

BASE_STYLE = """
<style>
:root {
    color-scheme: light;
}
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background-color: white;
}
</style>
"""
st.markdown(BASE_STYLE, unsafe_allow_html=True)

APP_PASSWORD = st.secrets["APP_PASSWORD"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ============================
# LOGIN
# ============================
if not st.session_state.authenticated:
    LOGIN_STYLE = """
    <style>
        .block-container {
            max-width: 420px !important;
            padding-top: 12vh;
            padding-bottom: 8vh;
        }
        .login-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 2.4rem 2.2rem;
            border: 1px solid #dfe4ef;
            box-shadow: 0 20px 55px rgba(15, 23, 42, 0.08);
        }
        .login-card h2 {
            font-size: 1.6rem;
            color: #1f2a44;
            margin-bottom: 0.4rem;
        }
        .login-card p {
            color: #4a5771;
            margin-bottom: 1.5rem;
        }
        .stButton > button {
            width: 100%;
            border-radius: 12px;
            padding: 0.8rem 1.2rem;
            border: none;
            background: #2957ff;
            color: white;
            font-weight: 600;
            transition: background 0.2s ease;
        }
        .stButton > button:hover {
            background: #1f46d2;
        }
    </style>
    """
    st.markdown(LOGIN_STYLE, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<h2>Accesso riservato</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p>Inserisci la password per accedere al planner editoriale Local SEO.</p>",
            unsafe_allow_html=True
        )
        pwd = st.text_input("Password", type="password")
        if st.button("Accedi"):
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.success("Accesso effettuato.")
                st.rerun()
            else:
                st.error("Password errata. Riprova.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ============================
# STILI APP
# ============================
APP_STYLE = """
<style>
.block-container {
    max-width: 1200px !important;
    padding: 2.5rem 3rem;
}
.header-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 1.8rem 2.2rem;
    border: 1px solid #e2e7f2;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
    margin-bottom: 1.8rem;
}
.header-card h1 {
    margin: 0;
    font-size: 2rem;
    color: #1f2942;
}
.header-card p {
    margin: 0.45rem 0 0;
    color: #49536b;
}

.info-card, .form-card, .result-card, .download-card, .utility-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.6rem 1.9rem;
    border: 1px solid #e2e7f2;
    box-shadow: 0 14px 35px rgba(15, 23, 42, 0.05);
    margin-bottom: 1.5rem;
}
.info-card h4 {
    margin-bottom: 0.8rem;
    font-size: 1.1rem;
    color: #1f2942;
}
.info-card ul {
    padding-left: 1.1rem;
    margin: 0;
    color: #53607a;
}
.info-card li {
    margin-bottom: 0.4rem;
}

.utility-card h4 {
    margin-bottom: 0.7rem;
    color: #1f2942;
}
.utility-card p {
    color: #53607a;
    margin-bottom: 1rem;
}

.form-card h3 {
    margin-bottom: 0.2rem;
    color: #1f2942;
}
.form-card p.section-subtitle {
    color: #5b6885;
    margin-bottom: 1.2rem;
}
.section-divider {
    border: none;
    border-top: 1px solid #e8ecf5;
    margin: 1.6rem 0 1.4rem;
}

.stRadio > label,
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label,
.stNumberInput > label {
    font-weight: 600;
    color: #2b3650;
}

.stForm > div button {
    border-radius: 14px !important;
    padding: 0.9rem 1.2rem !important;
    border: none !important;
    background: linear-gradient(135deg, #2957ff, #233fce) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 0.98rem !important;
}

.result-card h3, .download-card h3 {
    margin-bottom: 1rem;
    color: #1f2942;
}

.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #dfe4ef;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.6);
}

.download-card .stDownloadButton > button {
    width: 100%;
    border-radius: 12px;
    border: 1px solid #d0d9f0;
    background: #f3f6ff;
    color: #1f3bad;
    font-weight: 600;
    padding: 0.75rem 1.2rem;
}
.download-card .stDownloadButton > button:hover {
    border-color: #375fff;
}
.utility-card .stButton > button {
    width: 100%;
    border-radius: 12px;
    border: 1px solid #d0d9f0;
    background: #f3f6ff;
    color: #1f3bad;
    font-weight: 600;
    padding: 0.75rem 1.2rem;
}
.utility-card .stButton > button:hover {
    border-color: #375fff;
}

.stProgress > div > div {
    background-image: linear-gradient(90deg, #2a5af7, #476eff);
    border-radius: 12px;
}
.status-container {
    margin-bottom: 1.5rem;
}

@media (max-width: 980px) {
    .block-container {
        padding: 1.5rem;
    }
}
</style>
"""
st.markdown(APP_STYLE, unsafe_allow_html=True)

DATAFORSEO_LOGIN = st.secrets["DATAFORSEO_LOGIN"]
DATAFORSEO_PASSWORD = st.secrets["DATAFORSEO_PASSWORD"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ============================
# CHECK EXCEL
# ============================
try:
    import openpyxl
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

# ============================
# CACHE
# ============================
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=OPENAI_API_KEY)

# ============================
# API helper
# ============================
def fetch_serp(keyword, encoded_credentials, depth=5):
    url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
    headers = {"Authorization": f"Basic {encoded_credentials}", "Content-Type": "application/json"}
    payload = json.dumps([{
        "keyword": keyword,
        "location_code": 2380,
        "language_code": "it",
        "device": "desktop",
        "os": "windows",
        "depth": depth
    }])
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("status_code") == 20000:
            results = data["tasks"][0]["result"][0]["items"]
            return [r for r in results if r["type"] == "organic"][:depth]
    return []

def fetch_content_full(url, encoded_credentials):
    api_url = "https://api.dataforseo.com/v3/on_page/content_parsing/live"
    headers = {"Authorization": f"Basic {encoded_credentials}", "Content-Type": "application/json"}
    payload = json.dumps([{
        "url": url,
        "enable_javascript": True,
        "enable_browser_rendering": True
    }])
    response = requests.post(api_url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    return None

# ============================
# CLASSE PLANNER
# ============================
class LocalSEOPlanner:
    def __init__(self, login, password):
        credentials = f"{login}:{password}"
        self.encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.openai_client = get_openai_client()

    def get_serp_results(self, keyword):
        return fetch_serp(keyword, self.encoded_credentials, depth=5)

    def extract_text(self, url):
        data = fetch_content_full(url, self.encoded_credentials)
        if not data or data.get("status_code") != 20000:
            return ""
        result = data.get("result", [])
        if result and "items" in result[0]:
            items = result[0]["items"]
            if items and "page_content" in items[0]:
                page = items[0]["page_content"]
                text = ""
                for topic in page.get("main_topic", []):
                    for c in topic.get("primary_content", []):
                        if isinstance(c, dict) and c.get("text"):
                            text += c["text"] + " "
                return text[:4000]
        return ""

    def summarize_sources(self, topic, sources_text):
        prompt = f"""
Sei un analista Local SEO. Riassumi le informazioni più utili su "{topic}" basandoti sui testi forniti.
Sintesi 150-200 parole + 3-5 punti chiave.

TESTI:
{sources_text}

OUTPUT:
1. Sintesi
2. Punti chiave (bullet)
3. Località di riferimento
"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.9
        )
        return response.choices[0].message.content

    def generate_posts(self, business, sector, topic, brief, summary, n_posts,
                       target_location="", tone="professionale"):
        prompt = f"""
Agisci come un copywriter senior specializzato in Local SEO e Google Business Profile.

Obiettivo:
Generare {n_posts} post ottimizzati per Google Business Profile, pensati per aumentare visibilità locale e conversioni.

Dati azienda:
- Nome attività: {business}
- Settore: {sector}
- Argomento del post: {topic}
- Brief aggiuntivo: {brief}
- Informazioni di riferimento: {summary}
- Località target: {target_location or "N/D"}
- Tono richiesto: {tone}

Linee guida obbligatorie:
- Lunghezza: minimo 80, massimo 120 parole
- Tono: {tone}
- Linguaggio naturale, non artificiale
- Se la località target è valorizzata, inserire riferimenti locali solo a: "{target_location}"
- Se la località target è vuota, non inserire alcuna località
- Non usare altre località non fornite
- Non usare frasi tipiche degli LLM come "in conclusione"
- Evidenziare benefici concreti per il cliente
- CTA finale soft e locale (es. “Contattaci per maggiori informazioni”, “Vieni a trovarci”, “Chiama ora per una consulenza”)
- Ogni post deve essere diverso dagli altri per angolazione e struttura
- Evitare frasi generiche come: “leader del settore”, “massima qualità”, “anni di esperienza” se non supportate da dettagli
- Non usare emoji
- Non usare hashtag
- Non usare elenchi puntati
- Non inserire virgolette nel testo

Struttura consigliata:
1. Hook iniziale specifico e concreto
2. Sviluppo con valore pratico
3. Chiusura con CTA locale

Output:
Rispondi ESCLUSIVAMENTE in formato JSON valido, senza testo aggiuntivo prima o dopo:

{{
  "posts": [
    "Testo completo del post 1",
    "Testo completo del post 2"
  ]
}}
"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30000,
           _temperature=0.7
        )
        content = response.choices[0].message.content
        try:
            data = json.loads(content)
            return data.get("posts", [])
        except:
            parts = re.split(r"POST\s*\d+[:\-]", content)
            return [p.strip() for p in parts if p.strip()]

# ============================
# HEADER
# ============================
st.markdown(
    """
    <div class="header-card">
        <h1>Local SEO Editorial Planner</h1>
        <p>Genera post mirati per Google Business Profile partendo da analisi SERP e contenuti reali,
        con un flusso guidato e pronti all’uso.</p>
    </div>
    """,
    unsafe_allow_html=True
)

info_col, utility_col = st.columns([3, 1])
with info_col:
    st.markdown(
        """
        <div class="info-card">
            <h4>Come procedere</h4>
            <ul>
                <li>Compila i dati dell’attività (settore, sito, tono di voce).</li>
                <li>Inserisci gli argomenti: uno per riga se ne vuoi più di uno.</li>
                <li>Scegli se analizzare solo il tuo sito o l’intero web.</li>
                <li>Scarica il piano generato e adatta le date editoriali.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

with utility_col:
    st.markdown(
        """
        <div class="utility-card">
            <h4>Utility</h4>
            <p>Ripulisci la cache in caso di modifiche a prompt o risorse.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Svuota cache", key="clear_cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("Cache svuotata. Le prossime elaborazioni useranno solo dati aggiornati.")

# ============================
# FORM
# ============================
with st.form("planner_form"):
    st.markdown("<div class='form-card'>", unsafe_allow_html=True)

    st.markdown("<h3>1. Dati dell’attività</h3>", unsafe_allow_html=True)
    st.markdown("<p class='section-subtitle'>Informazioni necessarie per contestualizzare i contenuti.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        business = st.text_input("Nome azienda")
        sector = st.text_input("Settore / categoria")
        website = st.text_input("Sito web (es: https://www.sito.it)")
    with col2:
        target_location = st.text_input("Località target (es: Milano, Bologna…)")
        tone = st.selectbox(
            "Tono di voce",
            ["professionale", "tecnico", "divulgativo", "istituzionale", "commerciale"],
            index=0
        )
        n_posts = st.number_input("Numero post per argomento", min_value=1, max_value=20, value=3)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    st.markdown("<h3>2. Argomenti e brief</h3>", unsafe_allow_html=True)
    st.markdown("<p class='section-subtitle'>Inserisci uno o più argomenti (uno per riga) e note utili.</p>", unsafe_allow_html=True)

    topic_input = st.text_area("Argomento/i di riferimento", height=130, placeholder="Esempio:\nImpianti fotovoltaici residenziali\nManutenzione straordinaria impianti\nSoluzioni di storage per PMI")
    brief = st.text_area("Brief / informazioni aggiuntive", height=110, placeholder="Specifiche, promozioni, servizi distintivi, CTA desiderata…")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    st.markdown("<h3>3. Strategia di ricerca</h3>", unsafe_allow_html=True)
    source_mode = st.radio(
        "Fonte da cui estrarre insight",
        ["Dal sito web (site:)", "Dal web (query generica)"],
        horizontal=True
    )

    st.markdown("</div>", unsafe_allow_html=True)
    submit = st.form_submit_button("Genera piano editoriale")

# ============================
# SUBMIT LOGICA
# ============================
if submit:
    topics = [t.strip() for t in topic_input.split("\n") if t.strip()]
    if not topics:
        st.error("Inserisci almeno un argomento.")
        st.stop()

    if not business or not sector:
        st.error("Compila almeno nome azienda e settore.")
        st.stop()

    optimizer = LocalSEOPlanner(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD)

    rows = []
    total_steps = len(topics) * 3
    current_step = 0

    with st.status("Elaborazione in corso…", expanded=True) as status_box:
        progress = st.progress(0)
        for topic in topics:
            status_box.update(label=f"Analisi SERP per: **{topic}**")
            query = f"{topic} site:{website}" if source_mode.startswith("Dal sito") and website else topic
            serp = optimizer.get_serp_results(query)
            current_step += 1
            progress.progress(current_step / total_steps)

            status_box.update(label=f"Estrazione contenuti per: **{topic}**")
            sources_text = ""
            sources_urls = []
            for r in serp:
                sources_urls.append(r["url"])
                sources_text += optimizer.extract_text(r["url"]) + "\n"
            current_step += 1
            progress.progress(current_step / total_steps)

            status_box.update(label=f"Generazione post per: **{topic}**")
            summary = optimizer.summarize_sources(topic, sources_text)
            posts = optimizer.generate_posts(
                business, sector, topic, brief, summary,
                n_posts, target_location, tone
            )
            current_step += 1
            progress.progress(current_step / total_steps)

            for p in posts:
                rows.append({
                    "Data pubblicazione": "",
                    "Argomento": topic,
                    "Fonte": ", ".join(sources_urls) if sources_urls else "N/D",
                    "Contenuto post": p.strip(),
                    "Immagine": ""
                })

        status_box.update(label="Elaborazione completata.", state="complete")

    if not rows:
        st.warning("Nessun post generato. Verifica i dati inseriti e riprova.")
        st.stop()

    df = pd.DataFrame(rows)

    with st.container():
        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Piano editoriale generato</h3>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=420)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='download-card'>", unsafe_allow_html=True)
        st.markdown("<h3>Esporta</h3>", unsafe_allow_html=True)

        export_cols = st.columns(2)
        if EXCEL_AVAILABLE:
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)
            with export_cols[0]:
                st.download_button(
                    "Scarica Excel (.xlsx)",
                    data=buffer,
                    file_name="piano_editoriale_local_seo.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            with export_cols[0]:
                st.info("Per esportare in Excel installa openpyxl.", icon="ℹ️")

        csv = df.to_csv(index=False).encode("utf-8")
        with export_cols[1]:
            st.download_button(
                "Scarica CSV (.csv)",
                data=csv,
                file_name="piano_editoriale_local_seo.csv",
                mime="text/csv"
            )
        st.markdown("</div>", unsafe_allow_html=True)
