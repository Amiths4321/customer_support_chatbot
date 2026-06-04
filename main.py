import streamlit as st
import requests
import sys, io, threading, queue, os
import markdown as md_lib
from crew import run_pipeline

SKIP_FAMILIES = {"nomic-bert", "bert"}
SKIP_KEYWORDS = {"ocr", "embed", "vision", "vl", "coder", "sql", "code"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html,body,[class*="css"]{ font-family:'Inter',sans-serif !important; background:#07050f !important; }
[data-testid="collapsedControl"],section[data-testid="stSidebar"]{ display:none !important; }
#MainMenu,footer,header{ visibility:hidden !important; }
.block-container{ max-width:920px !important; padding:2rem 2rem 4rem !important; margin:0 auto !important; position:relative; z-index:1; }

@keyframes blobPulse{ from{transform:scale(1) rotate(0deg)} to{transform:scale(1.2) rotate(15deg)} }
@keyframes gradientShift{ 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
@keyframes float{ 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
@keyframes fadeUp{ from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }

body::before{ content:''; position:fixed; border-radius:50%; filter:blur(90px); pointer-events:none; z-index:0;
  animation:blobPulse 6s ease-in-out infinite alternate;
  width:500px; height:500px; top:-80px; left:-150px;
  background:radial-gradient(circle,#f43f5e 0%,#ec4899 35%,#a855f7 70%,transparent 100%); opacity:0.5; }
body::after{ content:''; position:fixed; border-radius:50%; filter:blur(90px); pointer-events:none; z-index:0;
  animation:blobPulse 7s ease-in-out infinite alternate-reverse;
  width:460px; height:460px; bottom:-100px; right:-130px;
  background:radial-gradient(circle,#06b6d4 0%,#3b82f6 35%,#6d28d9 70%,transparent 100%); opacity:0.5; }
.stApp::before{ content:''; position:fixed; border-radius:50%; filter:blur(80px); pointer-events:none; z-index:0;
  animation:blobPulse 9s ease-in-out infinite alternate;
  width:340px; height:340px; top:40%; right:-90px;
  background:radial-gradient(circle,#10b981 0%,#06b6d4 50%,transparent 100%); opacity:0.35; }
.stApp::after{ content:''; position:fixed; border-radius:50%; filter:blur(80px); pointer-events:none; z-index:0;
  animation:blobPulse 8s ease-in-out infinite alternate-reverse;
  width:300px; height:300px; top:55%; left:-70px;
  background:radial-gradient(circle,#f59e0b 0%,#f43f5e 50%,transparent 100%); opacity:0.32; }

.hero{ background:linear-gradient(270deg,#064e3b,#065f46,#0d9488,#0891b2,#1d4ed8,#4f46e5,#0d9488);
  background-size:400% 400%; animation:gradientShift 10s ease infinite;
  border-radius:28px; padding:44px 40px 36px; margin-bottom:28px; text-align:center; position:relative; overflow:hidden; }
.hero::before{ content:''; position:absolute; inset:0;
  background:radial-gradient(ellipse at top,rgba(255,255,255,0.1) 0%,transparent 65%); }
.hero-icon{ font-size:3rem; animation:float 3s ease-in-out infinite; display:block; margin-bottom:10px; }
.hero h1{ color:#fff; font-size:2.5rem; font-weight:900; margin:0 0 8px; letter-spacing:-0.02em; text-shadow:0 2px 20px rgba(0,0,0,0.3); }
.hero p{ color:rgba(255,255,255,0.82); font-size:0.98rem; margin:0; }

.stTextInput input{ background:#fff !important; border:2px solid rgba(16,185,129,0.4) !important;
  border-radius:14px !important; color:#111 !important; font-size:1.1rem !important; padding:15px 20px !important; }
.stTextInput input:focus{ border-color:#10b981 !important; box-shadow:0 0 0 4px rgba(16,185,129,0.15) !important; }
.stTextInput input::placeholder{ color:#aaa !important; }
.stTextInput label{ color:rgba(200,200,220,0.7) !important; font-size:0.85rem !important; }

.stButton>button{ background:linear-gradient(135deg,#065f46,#0d9488) !important;
  color:white !important; border:none !important; border-radius:14px !important;
  padding:13px 28px !important; font-weight:700 !important; font-size:1rem !important;
  width:100% !important; transition:all 0.25s !important; box-shadow:0 4px 20px rgba(13,148,136,0.4) !important; }
.stButton>button:hover{ transform:translateY(-3px) !important; box-shadow:0 8px 28px rgba(13,148,136,0.55) !important; }

.pipeline{ display:flex; gap:0; margin:24px 0; }
.agent-card{ flex:1; text-align:center; padding:18px 10px; border-radius:0; position:relative; }
.agent-card:first-child{ border-radius:16px 0 0 16px; }
.agent-card:last-child{ border-radius:0 16px 16px 0; }
.agent-card .icon{ font-size:1.8rem; display:block; margin-bottom:6px; }
.agent-card .name{ font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; }
.agent-card .role{ font-size:0.68rem; opacity:0.75; margin-top:2px; }
.agent-card.active{ transform:scale(1.06); z-index:2; box-shadow:0 8px 28px rgba(0,0,0,0.4); }
.a1{ background:linear-gradient(135deg,#1e3a5f,#1e40af); color:#93c5fd; }
.a2{ background:linear-gradient(135deg,#3b0764,#6d28d9); color:#c4b5fd; }
.a3{ background:linear-gradient(135deg,#7c2d12,#c2410c); color:#fed7aa; }
.a4{ background:linear-gradient(135deg,#064e3b,#065f46); color:#6ee7b7; }

.arrow{ display:flex; align-items:center; color:rgba(255,255,255,0.3); font-size:1.2rem; padding:0 4px; }

.log-box{ background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.07); border-radius:14px;
  padding:16px 20px; font-family:monospace; font-size:0.8rem; color:rgba(180,220,180,0.85);
  max-height:280px; overflow-y:auto; white-space:pre-wrap; word-break:break-word; margin-bottom:18px; }

.neon-hr{ height:1px; border:none; margin:24px 0;
  background:linear-gradient(90deg,transparent,#10b981,#0891b2,#6366f1,transparent); opacity:0.5; }

.tag{ display:inline-flex; align-items:center; gap:5px; padding:5px 14px; border-radius:20px;
  font-size:0.75rem; font-weight:700; letter-spacing:0.07em; text-transform:uppercase; margin-bottom:14px; }
.tag-green{ background:linear-gradient(135deg,#065f46,#0d9488); color:#fff; }
.tag-blue{ background:linear-gradient(135deg,#1e40af,#4f46e5); color:#fff; }
.tag-orange{ background:linear-gradient(135deg,#92400e,#d97706); color:#fff; }

.article-box{ background:linear-gradient(160deg,#050d1a,#030a14);
  border:1px solid rgba(16,185,129,0.25); border-radius:24px; padding:40px 44px;
  animation:fadeUp 0.5s ease; position:relative; overflow:hidden;
  box-shadow:0 0 0 1px rgba(16,185,129,0.06),0 24px 64px rgba(0,0,0,0.5); }
.article-box::before{ content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg,transparent,#10b981,#0d9488,#0891b2,transparent); }
.article-box h1{ color:#6ee7b7; font-size:1.6rem; font-weight:900; }
.article-box h2{ color:#34d399; font-size:1.2rem; font-weight:800; margin:24px 0 10px; border-bottom:1px solid rgba(52,211,153,0.2); padding-bottom:5px; }
.article-box h3{ color:#6ee7b7; font-size:1.05rem; font-weight:700; }
.article-box p,.article-box li{ color:#d4fce9; font-size:1.1rem; line-height:1.9; }
.article-box strong{ color:#a7f3d0; }
.article-box ul,.article-box ol{ padding-left:22px; }
.article-box li{ margin:7px 0; }

.stProgress>div>div{ background:linear-gradient(90deg,#10b981,#0d9488) !important; border-radius:4px !important; }
.stSpinner>div{ border-top-color:#10b981 !important; }
.stTabs [data-baseweb="tab-list"]{ background:rgba(255,255,255,0.04); border-radius:12px; padding:6px; }
.stTabs [data-baseweb="tab"]{ color:rgba(200,220,200,0.7) !important; border-radius:8px !important; font-weight:600 !important; }
.stTabs [aria-selected="true"]{ background:linear-gradient(135deg,#065f46,#0d9488) !important; color:#fff !important; }
</style>
"""

st.set_page_config(page_title="Content Pipeline", page_icon="🏭", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <span class="hero-icon">🏭</span>
  <h1>Multi-Agent Content Pipeline</h1>
  <p>4 AI agents collaborate: Research → Write → Review → Save</p>
</div>
""", unsafe_allow_html=True)

# ── Pipeline diagram ─────────────────────────────────────────────────────────
def pipeline_html(active: int = -1):
    agents = [
        ("🔍", "Researcher",  "Finds facts & sources",  "a1"),
        ("✍️", "Writer",      "Drafts the article",     "a2"),
        ("🧐", "Reviewer",    "Polishes & improves",    "a3"),
        ("💾", "Saver",       "Formats & saves",        "a4"),
    ]
    cards = []
    for i, (icon, name, role, cls) in enumerate(agents):
        ac = " active" if i == active else ""
        cards.append(f'<div class="agent-card {cls}{ac}"><span class="icon">{icon}</span><div class="name">{name}</div><div class="role">{role}</div></div>')
        if i < len(agents)-1:
            cards.append('<div class="arrow">›</div>')
    return f'<div class="pipeline">{"".join(cards)}</div>'

st.markdown(pipeline_html(), unsafe_allow_html=True)

# ── Server config ─────────────────────────────────────────────────────────────
with st.expander("⚙️ Ollama Server Settings"):
    c1, c2 = st.columns([3,1])
    server_ip   = c1.text_input("IP", value="10.22.39.192", placeholder="IP or localhost", label_visibility="collapsed")
    server_port = c2.text_input("Port", value="11434", label_visibility="collapsed")

ollama_base = f"http://{server_ip}:{server_port}"

def test_conn(url):
    try:
        r = requests.get(f"{url}/api/tags", timeout=4)
        return r.status_code == 200, None
    except requests.exceptions.ConnectionError:
        return False, "Cannot reach Ollama server."
    except requests.exceptions.Timeout:
        return False, "Connection timed out."
    except Exception as e:
        return False, str(e)

ok, err = test_conn(ollama_base)
if ok:
    st.success(f"✅ Connected to Ollama at `{ollama_base}`")
else:
    st.error(f"❌ {err}")
    st.info("Run `ollama serve` locally and set IP to `localhost`.")

@st.cache_data(ttl=30)
def fetch_models(url):
    try:
        r = requests.get(f"{url}/api/tags", timeout=4)
        names = [m["name"] for m in r.json().get("models",[])
                 if (m.get("details") or {}).get("family","") not in SKIP_FAMILIES
                 and not any(k in m["name"].lower() for k in SKIP_KEYWORDS)]
        return names or ["mistral:latest"]
    except Exception:
        return ["mistral:latest"]

models    = fetch_models(ollama_base)
preferred = next((m for m in models if "mistral" in m), models[0])

# ── Inputs ────────────────────────────────────────────────────────────────────
st.markdown('<div class="neon-hr"></div>', unsafe_allow_html=True)
topic = st.text_input("Article topic", placeholder="e.g. The future of AI in healthcare, Climate change solutions, Quantum computing…")

ca, cb = st.columns([3,1])
with cb:
    model = st.selectbox("Model", models, index=models.index(preferred), label_visibility="collapsed")
with ca:
    run = st.button("🚀 Run Pipeline", disabled=not ok)

# ── Run ───────────────────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.warning("Please enter a topic.")
    else:
        st.markdown('<div class="neon-hr"></div>', unsafe_allow_html=True)

        pipeline_placeholder = st.empty()
        log_placeholder      = st.empty()
        status_placeholder   = st.empty()

        agent_labels = ["Researcher", "Writer", "Reviewer", "Saver"]
        log_lines    = []

        class StreamCapture(io.StringIO):
            def write(self, txt):
                if txt.strip():
                    log_lines.append(txt.rstrip())
                    log_placeholder.markdown(
                        f'<div class="log-box">{"<br>".join(log_lines[-30:])}</div>',
                        unsafe_allow_html=True
                    )
                return super().write(txt)

        result = {}

        def _run():
            old_stdout = sys.stdout
            sys.stdout = StreamCapture()
            try:
                result.update(run_pipeline(topic.strip(), ollama_base, model))
            except Exception as e:
                result["error"] = str(e)
            finally:
                sys.stdout = old_stdout

        stages = [
            (0, "🔍 Agent 1: Researching the topic…"),
            (1, "✍️ Agent 2: Writing the article…"),
            (2, "🧐 Agent 3: Reviewing and polishing…"),
            (3, "💾 Agent 4: Formatting and saving…"),
        ]

        # Run in thread so Streamlit can update UI
        t = threading.Thread(target=_run, daemon=True)
        t.start()

        import time
        stage_idx = 0
        while t.is_alive():
            if stage_idx < len(stages):
                idx, label = stages[stage_idx]
                pipeline_placeholder.markdown(pipeline_html(idx), unsafe_allow_html=True)
                status_placeholder.markdown(f'<span class="tag tag-green">⚡ {label}</span>', unsafe_allow_html=True)
                # Advance stage roughly every ~90 seconds
                time.sleep(90)
                stage_idx += 1
            else:
                time.sleep(5)
        t.join()

        pipeline_placeholder.markdown(pipeline_html(-1), unsafe_allow_html=True)
        log_placeholder.empty()
        status_placeholder.empty()

        if "error" in result:
            st.error(f"Pipeline error: {result['error']}")
        else:
            st.markdown('<span class="tag tag-green">✅ Pipeline Complete</span>', unsafe_allow_html=True)

            tabs = st.tabs(["📰 Final Article", "🔍 Research Notes", "📝 First Draft", "🧐 Reviewed Draft"])

            def render(text):
                try:    return md_lib.markdown(text or "", extensions=["extra","nl2br"])
                except: return (text or "").replace("\n","<br>")

            with tabs[0]:
                st.markdown(f'<div class="article-box">{render(result.get("final",""))}</div>', unsafe_allow_html=True)
                st.download_button("📥 Download Article", data=result.get("final",""),
                                   file_name=f"{topic[:40].replace(' ','_')}_article.md", mime="text/markdown")

            with tabs[1]:
                st.markdown(f'<div class="article-box">{render(result.get("research",""))}</div>', unsafe_allow_html=True)
            with tabs[2]:
                st.markdown(f'<div class="article-box">{render(result.get("draft",""))}</div>', unsafe_allow_html=True)
            with tabs[3]:
                st.markdown(f'<div class="article-box">{render(result.get("reviewed",""))}</div>', unsafe_allow_html=True)

            # Show saved file location
            output_files = sorted([f for f in os.listdir("output") if f.endswith(".md")], reverse=True) if os.path.exists("output") else []
            if output_files:
                st.caption(f"💾 Saved to: `output/{output_files[0]}`")
