import streamlit as st
import base64, json, requests, re
from typing import List
from openai import OpenAI
from io import BytesIO
import pandas as pd

# ============================
# CONFIGURAZIONE PAGINA & STILE
# ============================
st.set_page_config(
    page_title="Local SEO Editorial Planner",
    page_icon="📍",
    layout="wide"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding: 2.5rem 4rem 3rem;
        background: #f5f7fb;
    }
    .hero {
        background: linear-gradient(135deg, rgba(34, 106, 228, 0.15), rgba(61, 138, 255, 0.25));
        border-radius: 24px;
        padding: 2.5rem 3rem;
        box-shadow: 0 18px 45px rgba(32, 68, 162, 0.08);
        margin-bottom: 2rem;
        color: #0f1a3c;
    }
    .hero h1 {
        font-weight: 700;
        font-size: 2.4rem;
        margin-bottom: 0.6rem;
    }
    .hero p {
        font-size: 1rem;
        color: #2d4271;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 1.8rem 2rem;
        box-shadow: 0 22px 50px rgba(15, 23, 42, 0.06);
        border: 1px solid rgba(152, 175, 233, 0.15);
        margin-bottom: 1.4rem;
    }
    .glass-card h3 {
        font-weight: 600;
        margin-bottom: 1.2rem;
        color: #183169;
    }
    .glow-button > button {
        width: 100%;
        padding: 0.9rem 1.3rem;
        border-radius: 16px;
        border: none;
        background: linear-gradient(135deg, #1f60ff, #2344d2);
        color: white;
        font-weight: 600;
        font-size: 0.98rem;
        box-shadow: 0 20px 35px rgba(35, 76, 215, 0.35);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .glow-button > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 24px 45px rgba(35, 76, 215, 0.45);
    }
    .login-card {
        max-width: 450px;
        margin: 3rem auto;
        border-radius: 22px;
        padding: 2.6rem 2.4rem;
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 26px 70px rgba(15, 23, 42, 0.12);
        border: 1px solid rgba(152, 175, 233, 0.2);
    }
    .hint-box {
        background: rgba(48, 94, 223, 0.08);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(48, 94, 223, 0.18);
        color: #173372;
    }
    .download-box {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .download-card {
        flex: 1 1 260px;
        background: white;
        border-radius: 18px;
        padding: 1.5rem 1.6rem;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
        border: 1px solid rgba(152, 175, 233, 0.18);
    }
    .download-card h4 {
        margin: 0 0 0.4rem;
        font-weight: 600;
    }
    .download-card small {
        display: block;
        color: #5b6b88;
        margin-bottom: 1.1rem;
    }
    .download-card .stDownloadButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(35, 82, 231, 0.35);
        padding: 0.65rem 1.2rem;
        color: #1d3c9d;
        font-weight: 600;
        background: rgba(35, 82, 231, 0.08);
    }
    .download-card .stDownloadButton > button:hover {
        border-color: rgba(35, 82, 231, 0.5);
        background: rgba(35, 82, 231, 0.15);
    }
    .stRadio > label {font-weight: 500; color: #1a2d54;}
    .stTextInput > label, .stTextArea > label, .stSelectbox > label {
        font-weight: 500;
        color: #1a2d54;
    }
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(164, 181, 219, 0.45);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
    }
    .stProgress > div > div {
        background-image: linear-gradient(90deg, #3a66f2, #5f82ff);
        border-radius: 20px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

APP_PASSWORD = st.secrets["APP_PASSWORD"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ============================
# LOGIN
# ============================
if not st.session_state.authenticated:
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Accesso riservato")
    st.write("Inserisci la password per accedere al planner editoriale Local SEO.")
    pwd = st.text_input("Password", type="password")
    if st.button("Accedi", use_container_width=True):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.success("Accesso effettuato!")
            st.rerun()
        else:
            st.error("Password errata. Riprova.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

DATAFORSEO_LOGIN = st.secrets["DATAFORSEO_LOGIN"]
DATAFORSEO_PASSWORD = st.secrets["DATAFORSEO_PASSWORD"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ============================
# CHECK EXCEL SUPPORT
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
# NIENTE CACHE per SERP e PARSING
# ============================
def fetch_serp(keyword, encoded_credentials, depth=5):
    url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }
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
# CLASSE PRINCIPALE
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

    def generate_posts(self, business, sector, topic, brief, summary, n_posts, target_location="", tone="professionale"):
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
            temperature=0.7
        )
        content = response.choices[0].message.content
        try:
            data = json.loads(content)
            return data.get("posts", [])
        except:
            parts = re.split(r"POST\s*\d+[:\-]", content)
            return [p.strip() for p in parts if p.strip()]

# ============================
# HERO & INTRO
# ============================
st.markdown(
    """
    <div class="hero">
        <h1>Local SEO Editorial Planner</h1>
        <p>
            Genera post mirati per Google Business Profile partendo da analisi SERP, contenuti reali e insight locali.
            Personalizza argomenti, tono di voce e ricevi un piano editoriale pronto da pubblicare.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("💡 Suggerimenti rapidi", expanded=True):
    st.markdown(
        """
        - Inserisci argomenti specifici e, se possibile, legati ai servizi chiave dell’azienda.
        - Scegli il tono più adatto al tuo target (professionale, divulgativo, tecnico…).
        - Seleziona “Dal sito web” per valorizzare i contenuti proprietari, “Dal web” per trend e competitor.
        """
    )

# Pulsante opzionale per svuotare cache
top_cols = st.columns([6, 1])
with top_cols[1]:
    if st.button("Ripulisci cache"):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.toast("Cache svuotata. I prossimi dati saranno aggiornati.", icon="🧼")

# ============================
# FORM PRINCIPALE
# ============================
with st.form("planner_form"):
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Configurazione")

    col1, col2 = st.columns(2)
    with col1:
        business = st.text_input("Nome azienda")
        sector = st.text_input("Settore")
        website = st.text_input("Sito web (es: https://www.sito.it)")
        target_location = st.text_input("Località target (es: Milano, Bologna, ecc.)")
    with col2:
        tone = st.selectbox("Tono di voce", ["professionale", "tecnico", "divulgativo", "istituzionale", "commerciale"])
        topic_mode = st.selectbox("Modalità argomenti", ["Singolo argomento", "Lista di argomenti"])
        topic_input = st.text_area("Argomento/i (uno per riga)", height=150)
        n_posts = st.number_input("Numero post per argomento", 1, 20, 3)
        brief = st.text_area("Brief / informazioni aggiuntive", height=110)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🔎 Fonti e ricerca")
    source_mode = st.radio(
        "Scegli la fonte principale",
        ["Dal sito web (site:)", "Dal web (query generica)"],
        horizontal=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glow-button'>", unsafe_allow_html=True)
    submit = st.form_submit_button("Genera piano editoriale")
    st.markdown("</div>", unsafe_allow_html=True)

if submit:
    optimizer = LocalSEOPlanner(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD)

    topics = [t.strip() for t in topic_input.split("\n") if t.strip()]
    if not topics:
        st.error("Inserisci almeno un argomento.")
        st.stop()

    rows = []

    with st.status("⏳ Elaborazione in corso…", expanded=True) as status_box:
        total_steps = len(topics) * 3
        progress = st.progress(0)
        current_step = 0

        for topic in topics:
            status_box.update(label=f"🔍 SERP in analisi per **{topic}**")
            query = f"{topic} site:{website}" if source_mode.startswith("Dal sito") else topic
            serp = optimizer.get_serp_results(query)
            current_step += 1
            progress.progress(current_step / total_steps)

            status_box.update(label=f"🧾 Contenuti estratti per **{topic}**")
            sources_text = ""
            sources_urls = []
            for r in serp:
                sources_urls.append(r["url"])
                sources_text += optimizer.extract_text(r["url"]) + "\n"
            current_step += 1
            progress.progress(current_step / total_steps)

            status_box.update(label=f"✍️ Post generati per **{topic}**")
            summary = optimizer.summarize_sources(topic, sources_text)
            posts = optimizer.generate_posts(
                business, sector, topic, brief, summary, n_posts, target_location, tone
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

        status_box.update(label="✅ Piano completato!", state="complete")

    st.toast("Piano editoriale generato con successo!", icon="🚀")
    df = pd.DataFrame(rows)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📅 Piano editoriale")
    st.dataframe(df, use_container_width=True, height=420)
    st.markdown("</div>", unsafe_allow_html=True)

    # ===== EXPORT =====
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📦 Esporta il risultato")
    st.markdown("<div class='download-box'>", unsafe_allow_html=True)

    if EXCEL_AVAILABLE:
        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        st.markdown("<div class='download-card'>", unsafe_allow_html=True)
        st.markdown("#### Excel")
        st.markdown("<small>File strutturato con fogli modificabili</small>", unsafe_allow_html=True)
        st.download_button(
            "Scarica .xlsx",
            data=buffer,
            file_name="piano_editoriale_local_seo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ openpyxl non installato. Attiva il CSV oppure aggiungi openpyxl alle dipendenze.")

    csv = df.to_csv(index=False).encode("utf-8")
    st.markdown("<div class='download-card'>", unsafe_allow_html=True)
    st.markdown("#### CSV")
    st.markdown("<small>Formato universale per tutti i fogli di calcolo</small>", unsafe_allow_html=True)
    st.download_button(
        "Scarica .csv",
        data=csv,
        file_name="piano_editoriale_local_seo.csv",
        mime="text/csv",
        use_container_width=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
