import streamlit as st
import base64, json, requests, time, re
from typing import List
from openai import OpenAI
from io import BytesIO
import pandas as pd

# ============================
# SECRETS
# ============================
DATAFORSEO_LOGIN = st.secrets["DATAFORSEO_LOGIN"]
DATAFORSEO_PASSWORD = st.secrets["DATAFORSEO_PASSWORD"]
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

APP_PASSWORD = st.secrets["APP_PASSWORD"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Accesso protetto")
    pwd = st.text_input("Inserisci la password", type="password")
    if st.button("Entra"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Password errata")
    st.stop()

# ============================
# CACHE
# ============================
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key=OPENAI_API_KEY)

@st.cache_data(ttl=3600)
def cached_serp(keyword, encoded_credentials, depth=5):
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

@st.cache_data(ttl=3600)
def cached_content_full(url, encoded_credentials):
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
        return cached_serp(keyword, self.encoded_credentials, depth=5)

    def extract_text(self, url):
        data = cached_content_full(url, self.encoded_credentials)
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
Sei un analista SEO. Riassumi le informazioni più utili su "{topic}" basandoti sui testi forniti.
Sintesi 150-200 parole + 3-5 punti chiave.

TESTI:
{sources_text}

OUTPUT:
1. Sintesi
2. Punti chiave (bullet)
"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role":"user","content":prompt}],
            max_tokens=1200,
            temperature=0.5
        )
        return response.choices[0].message.content

    def generate_posts(self, business, sector, topic, brief, summary, n_posts):
        prompt = f"""
Sei un copywriter Local SEO esperto.
Genera {n_posts} post per Google Business Profile.

Azienda: {business}
Settore: {sector}
Argomento: {topic}
Brief aggiuntivo: {brief}
Informazioni di riferimento: {summary}

Regole:
- 80-120 parole
- tono professionale
- CTA locale soft (contattaci, vieni in sede, ecc.)
- nessuna frase generica

Rispondi SOLO in JSON:
{{
  "posts": ["testo post 1", "testo post 2", ...]
}}
"""
        response = self.openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role":"user","content":prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        content = response.choices[0].message.content
        try:
            data = json.loads(content)
            return data.get("posts", [])
        except:
            # fallback parsing
            parts = re.split(r"POST\s*\d+[:\-]", content)
            return [p.strip() for p in parts if p.strip()]

# ============================
# STREAMLIT UI
# ============================
st.set_page_config(page_title="Local SEO Editorial Planner", layout="wide")
st.title("📍 Local SEO Editorial Planner")

with st.expander("ℹ️ Come funziona?"):
    st.write("""
    Inserisci i dati aziendali, scegli gli argomenti e il numero di post.
    L'app cerca contenuti nel sito o nel web, li riassume e genera i post.
    Output finale: Excel con piano editoriale.
    """)

with st.form("planner_form"):
    business = st.text_input("Nome azienda")
    sector = st.text_input("Settore")
    website = st.text_input("Sito web (es: https://www.sito.it)")
    
    topic_mode = st.selectbox("Argomenti", ["Singolo argomento", "Lista di argomenti"])
    topic_input = st.text_area("Inserisci argomento/i (uno per riga)")
    n_posts = st.number_input("Numero post per argomento", 1, 20, 3)
    brief = st.text_area("Brief / informazioni aggiuntive")
    source_mode = st.radio("Fonte info", ["Dal sito web (site:)", "Dal web (query generica)"])
    submit = st.form_submit_button("Genera piano editoriale")

if submit:
    optimizer = LocalSEOPlanner(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD)

    topics = [t.strip() for t in topic_input.split("\n") if t.strip()]
    if not topics:
        st.error("Inserisci almeno un argomento")
        st.stop()

    rows = []
    for topic in topics:
        query = f"{topic} site:{website}" if source_mode.startswith("Dal sito") else topic
        serp = optimizer.get_serp_results(query)

        sources_text = ""
        sources_urls = []
        for r in serp:
            sources_urls.append(r["url"])
            sources_text += optimizer.extract_text(r["url"]) + "\n"

        summary = optimizer.summarize_sources(topic, sources_text)
        posts = optimizer.generate_posts(business, sector, topic, brief, summary, n_posts)

        for p in posts:
            rows.append({
                "Data pubblicazione": "",
                "Argomento": topic,
                "Fonte": ", ".join(sources_urls),
                "Contenuto post": p.strip(),
                "Immagine": ""
            })

    df = pd.DataFrame(rows)
    st.success("✅ Piano editoriale generato!")
    st.dataframe(df, use_container_width=True)

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        "⬇️ Scarica Excel",
        data=buffer,
        file_name="piano_editoriale_local_seo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
