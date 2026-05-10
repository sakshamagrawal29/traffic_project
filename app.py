"""
Traffic Prediction System — Streamlit Dashboard
Fixed: clock auto-refresh, icon rendering, sidebar gap, hover tooltip,
       card jitter, all 9 pages implemented, weather mock label.
"""
import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import textwrap

# ── helper: strip Python indentation before passing HTML to st.markdown
# Without this, lines indented 4+ spaces become Markdown code blocks
def html(s: str) -> None:
    st.markdown(textwrap.dedent(s).strip(), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Traffic Prediction System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  MODEL
# ══════════════════════════════════════════════════════════════
try:
    model = joblib.load("traffic_model.pkl")
except Exception as _e:
    st.error(f"⚠️  Model load failed — {_e}")
    st.stop()

# ══════════════════════════════════════════════════════════════
#  CSS  (plain string — NOT an f-string so CSS braces need no escaping)
#
#  Fix summary baked into CSS:
#  • Sidebar gap  → box-shadow on sidebar + left padding on stMain
#  • Hover jitter → removed translateY from card hover (box-shadow only)
#  • Tooltip dbl  → pointer-events:none on radio <p>, suppressed baseweb tooltip
#  • Responsive   → @media queries for narrow screens
# ══════════════════════════════════════════════════════════════
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
      rel="stylesheet"/>
<style>

/* ── RESET STREAMLIT CHROME ────────────────────────────────── */
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }
/* Hide the sidebar's internal ← collapse button so it can never be accidentally collapsed.
   Do NOT hide collapsedControl — that's the ☰ re-open button; hiding it locks users out. */
[data-testid="stSidebarCollapseButton"] { display: none !important; }

/* ── GLOBAL ────────────────────────────────────────────────── */
*, *::before, *::after { font-family: 'Poppins', sans-serif !important; box-sizing: border-box; }
body { background: #070F1F !important; margin: 0; padding: 0; }
.stApp, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0b132b 0%, #1c2541 50%, #3a506b 100%) !important;
}

/* ── FIX 1: SIDEBAR GAP ────────────────────────────────────── */
/* box-shadow on sidebar creates visible depth / separation     */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141E30 0%, #243B55 100%) !important;
    border-right: 1px solid #243041 !important;
    box-shadow: 6px 0 28px rgba(0,0,0,0.45) !important; /* ← gap via shadow depth */
    min-width: 245px !important;
    max-width: 245px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 16px 12px 24px !important; }

/* FIX 1b: padding-left on stMain separates content from sidebar border */
[data-testid="stMain"] { padding-left: 0.75rem !important; padding-top: 0 !important; }
.block-container        { padding: 0 2rem 3rem 1.5rem !important; max-width: 100% !important; }

/* ── SIDEBAR RADIO → NAV ITEMS ─────────────────────────────── */
/* FIX 2/5: st.radio styled as nav items with NO transform
   (transform causes double-paint + sidebar collapse on click)  */
[data-testid="stSidebar"] [data-testid="stRadio"]        { width: 100% !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] > div  {
    display: flex !important; flex-direction: column !important; gap: 3px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important; align-items: center !important; gap: 10px !important;
    padding: 10px 14px !important; border-radius: 14px !important;
    color: rgba(255,255,255,0.82) !important;
    font-size: 14px !important; font-weight: 500 !important;
    cursor: pointer !important;
    transition: background 0.2s ease !important;
    user-select: none !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    /* NO transform: prevents double-paint and sidebar collapse */
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.09) !important;
    color: white !important;
}

/* FIX 5: suppress "double text" tooltip on radio label hover  */
[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    pointer-events: none !important;  /* prevents browser tooltip trigger */
}
/* BaseWeb tooltip portals render in <body>, NOT inside stSidebar —
   must use a global selector, not a scoped one */
[data-baseweb="tooltip"]                           { display: none !important; }
[data-testid="stTooltipContent"]                   { display: none !important; }

/* Hide radio circle bullet */
[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child,
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"] { display: none !important; }

/* Active nav item — CSS :has() (Chrome 105+, Firefox 121+, Safari 15.4+) */
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #6D5DFB !important;
    color: white !important;
}

/* Sidebar info card */
#side-card {
    margin-top: 20px;
    background: rgba(255,255,255,0.05);
    border: 1px solid #243041;
    border-radius: 18px;
    padding: 16px;
    text-align: center;
    transition: border-color 0.3s, box-shadow 0.3s;
}
#side-card:hover { border-color: rgba(109,93,251,0.5); box-shadow: 0 0 14px rgba(109,93,251,0.2); }
#side-card h4 { color: white !important; margin: 8px 0 4px; font-size: 13px; }
#side-card p  { color: #9CA3AF !important; font-size: 11px; margin: 0; }

/* ── NAVBAR ────────────────────────────────────────────────── */
#navbar {
    height: 70px; display: flex; align-items: center;
    padding: 0 24px; background: #0f1937; color: white;
    position: sticky; top: 0; z-index: 999; width: 100%;
    margin-bottom: 22px; box-shadow: 0 2px 18px rgba(0,0,0,0.45);
}
#logo                { display: flex; align-items: center; gap: 12px; }
#logo-text           { display: flex; flex-direction: column; }
#logo h1             { font-size: 19px; margin: 0; color: white !important; font-weight: 600; }
#logo p              { font-size: 11px; color: #9CA3AF; margin: 0; }
#logo-icon           { font-size: 26px; }
#nav-right           { display: flex; align-items: center; gap: 14px; margin-left: auto; }
.nav-pill {
    background: rgba(255,255,255,0.06); border: 1px solid #243041;
    border-radius: 100px; padding: 7px 14px;
    font-size: 13px; font-weight: 500; color: white; white-space: nowrap;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.nav-pill:hover { border-color: rgba(59,130,246,0.4); box-shadow: 0 0 8px rgba(59,130,246,0.2); }

/* ── FIX 8: CARD CONTAINERS — no translateY (prevents layout jitter) ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid #243041 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    padding: 16px !important;
    transition: border-color 0.3s, box-shadow 0.3s !important;
    /* translateY REMOVED — caused jitter during Streamlit re-renders */
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(59,130,246,0.38) !important;
    box-shadow: 0 0 20px rgba(59,130,246,0.18), 0 0 42px rgba(95,196,28,0.08) !important;
}
.card-title    { font-size: 18px; font-weight: 600; color: white !important; margin: 0 0 4px; }
.card-subtitle { font-size: 12px; color: #9CA3AF; margin: 0 0 16px; }

/* ── INPUT WIDGETS ─────────────────────────────────────────── */
.stSelectbox label, .stSlider label { color: #9CA3AF !important; font-size: 13px !important; font-weight: 400 !important; }
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.08) !important; color: white !important;
    border: 1px solid #243041 !important; border-radius: 10px !important;
}
[data-testid="stSelectbox"] svg                            { fill: #9CA3AF !important; }
.stSlider [role="slider"]                                  { background-color: #6D5DFB !important; }
[data-baseweb="slider"] div[data-baseweb="slider-track-fill"] { background: #6D5DFB !important; }

/* ── BUTTONS ───────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #6D5DFB, #4f46e5) !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    padding: 13px 24px !important; font-size: 15px !important; font-weight: 600 !important;
    width: 100% !important; margin-top: 14px !important; letter-spacing: 0.5px !important;
    transition: box-shadow 0.3s ease !important;
}
.stButton > button:hover  { box-shadow: 0 0 22px rgba(109,93,251,0.55) !important; }
.stButton > button:active { transform: scale(0.99) !important; }

/* ── RESULT / TRAFFIC LEVEL CARD ───────────────────────────── */
.result-content {
    display: flex; align-items: center; justify-content: space-between;
    gap: 14px; margin-top: 14px; flex-wrap: wrap;
}
.left-result { display: flex; flex-direction: column; align-items: center; }
.traffic-wrapper { position: relative; width: 108px; height: 108px; flex-shrink: 0; }
.ring {
    width: 108px; height: 108px; border-radius: 50%;
    background: conic-gradient(#22c55e, #facc15, #ff7b00, #ff3b3b, #22c55e);
    animation: rotateRing 6s linear infinite;
}
.ring::before { content: ""; position: absolute; inset: 10px; border-radius: 50%; background: #2c3858; }
.car-icon {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%); font-size: 26px; z-index: 5;
    animation: floatCar 2s ease-in-out infinite;
}
.traffic-level { font-size: 30px; letter-spacing: 2px; font-weight: 700; margin-top: 10px; text-align: center; }
.traffic-level.awaiting { color: #6B7280; }
.traffic-level.low    { background: linear-gradient(90deg,#22c55e,#16a34a);
                         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.traffic-level.medium { background: linear-gradient(90deg,#facc15,#f59e0b,#ff7b00);
                         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.traffic-level.high   { background: linear-gradient(90deg,#ffb800,#ff7b00,#ff3b3b);
                         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.traffic-status { color: #AEB6C8; font-size: 13px; margin-top: -4px; }

.traffic-info   { display: flex; flex-direction: column; gap: 10px; }
.info-box {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 10px 14px; min-width: 118px;
    transition: border-color 0.3s;
}
.info-box:hover  { border-color: rgba(109,93,251,0.45); }
.info-box h4     { font-size: 11px; color: #9CA3AF; margin: 0 0 4px; }
.info-box span   { color: white; font-size: 16px; font-weight: 600; }
.badge-high   { color:#ff6b6b!important; background:rgba(193,43,43,0.25);
                border-radius:8px; border:1px solid rgba(255,144,144,0.2);
                padding:3px 9px; font-size:.82rem; font-weight:700; }
.badge-medium { color:#facc15!important; background:rgba(234,179,8,0.2);
                border-radius:8px; border:1px solid rgba(234,179,8,0.3);
                padding:3px 9px; font-size:.82rem; font-weight:700; }
.badge-low    { color:#22c55e!important; background:rgba(34,197,94,0.2);
                border-radius:8px; border:1px solid rgba(34,197,94,0.3);
                padding:3px 9px; font-size:.82rem; font-weight:700; }

/* ── ALERT CARDS ───────────────────────────────────────────── */
.alert-card {
    background: rgba(255,255,255,0.04); border-left: 4px solid;
    border-radius: 12px; padding: 14px 18px; margin-bottom: 12px;
    transition: background 0.2s;
}
.alert-card:hover  { background: rgba(255,255,255,0.07); }
.alert-card.high   { border-color: #ff6b6b; }
.alert-card.medium { border-color: #facc15; }
.alert-card.low    { border-color: #22c55e; }
.alert-card .a-type { font-size: 11px; font-weight: 700; letter-spacing: 1px; }
.alert-card .a-msg  { color: white; font-size: 14px; margin: 4px 0; }
.alert-card .a-meta { color: #9CA3AF; font-size: 12px; }

/* ── METRIC CARDS ──────────────────────────────────────────── */
.metric-card {
    background: rgba(255,255,255,0.05); border: 1px solid #243041;
    border-radius: 14px; padding: 18px 20px; text-align: center;
}
.metric-card .m-val { font-size: 28px; font-weight: 700; color: white; }
.metric-card .m-lbl { font-size: 12px; color: #9CA3AF; margin-top: 4px; }

/* ── PAGE TITLES ───────────────────────────────────────────── */
.page-title { color: white !important; font-size: 22px; font-weight: 600; margin: 0 0 4px; }
.page-sub   { color: #9CA3AF; font-size: 13px; margin: 0 0 22px; }

/* ── PLOTLY / DATAFRAME / MISC ─────────────────────────────── */
.js-plotly-plot, .plot-container { background: transparent !important; }
[data-testid="stDataFrameResizable"] { border-radius: 12px !important; overflow: hidden; }
.stDataFrame th { background: #1c2541 !important; color: white !important; }
.stDataFrame td { color: #d1d5db !important; }
[data-testid="stDivider"] hr { border-color: #243041 !important; }
[data-testid="column"]       { padding: 0 6px !important; }
.section-gap                 { margin-top: 22px; }
.coming-soon { text-align: center; color: #9CA3AF; padding: 80px 20px; font-size: 48px; }
.coming-soon p { font-size: 15px; margin-top: 8px; }

/* ── RESPONSIVE ────────────────────────────────────────────── */
@media (max-width: 768px) {
    #navbar { height: auto; flex-wrap: wrap; gap: 8px; padding: 10px 12px; margin-bottom: 14px; }
    #nav-right { width: 100%; gap: 6px; }
    .nav-pill { font-size: 11px; padding: 5px 10px; }
    .result-content { flex-direction: column; align-items: center; }
    .traffic-info   { flex-direction: row; flex-wrap: wrap; }
    .block-container { padding: 0 0.75rem 2rem !important; }
}

/* ── ANIMATIONS ────────────────────────────────────────────── */
@keyframes rotateRing { from { transform: rotate(0deg); }   to { transform: rotate(360deg); } }
@keyframes floatCar {
    0%   { transform: translate(-50%, -50%); }
    50%  { transform: translate(-50%, -62%); }
    100% { transform: translate(-50%, -50%); }
}

</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SESSION STATE — initialise defaults once
# ══════════════════════════════════════════════════════════════
_DEFAULTS: dict = {
    "traffic_text":     "——",
    "traffic_class":    "awaiting",
    "traffic_value":    0,
    "traffic_color":    "#6B7280",
    "congestion_badge": '<span style="color:#9CA3AF;font-size:14px;">Awaiting</span>',
    "probability":      "—",
    "status_text":      "Run a prediction",
    "history":          [],
    "pref_city":        "Jaipur",
    "pref_notify":      True,
    "pref_compact":     False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════════════════════
#  FIX 6: NAVBAR with @st.fragment(run_every=30)
#  The fragment re-executes every 30 s without triggering a full
#  page rerun → time display stays current automatically.
#  FIX 10: Weather clearly labelled "(mock)" — not real sensor data.
# ══════════════════════════════════════════════════════════════
@st.fragment(run_every=30)
def _navbar() -> None:
    _t = datetime.now().strftime("%I:%M %p")
    _d = datetime.now().strftime("%d %b %Y")
    html(f"""
    <div id="navbar">
        <div id="logo">
            <span id="logo-icon">🚗</span>
            <div id="logo-text">
                <h1>Traffic Prediction System</h1>
                <p>Smart City, Better City</p>
            </div>
        </div>
        <div id="nav-right">
            <span class="nav-pill">
                🌤️ 28°C
                <span style="font-size:10px;color:#6B7280;margin-left:3px;">(mock)</span>
            </span>
            <span class="nav-pill">📅 {_d}</span>
            <span class="nav-pill">🕒 {_t}</span>
        </div>
    </div>
    """)

_navbar()

# ══════════════════════════════════════════════════════════════
#  SIDEBAR — st.radio styled as nav items
#
#  FIX 2: Removed variation-selector U+FE0F from ⚙️ and ℹ️.
#          On Linux/Streamlit Cloud those render as [] because the
#          system fonts only carry the text-presentation glyph.
#          Plain ⚙ (U+2699) and ℹ (U+2139) render everywhere.
#
#  FIX 4: st.radio gives real Python callbacks → pages switch
#          reliably. No onclick HTML, no query_params workarounds.
#
#  FIX 5: No transform on hover → sidebar never collapses.
# ══════════════════════════════════════════════════════════════
NAV_PAGES = [
    "🏠  Dashboard",
    "🔮  Prediction",
    "📈  Analytics",
    "📍  Traffic Map",
    "📜  History",
    "🔔  Alerts",
    "📊  Reports",
    "⚙  Settings",    # plain ⚙ (U+2699), no variation selector
    "ℹ  About",        # plain ℹ (U+2139), no variation selector
]

with st.sidebar:
    page = st.radio(
        "Navigation",
        NAV_PAGES,
        label_visibility="collapsed",
        key="nav",
    )
    html("""
        <div id="side-card">
            <div style="font-size:28px;">🤖</div>
            <h4>Smart Traffic AI</h4>
            <p>Predict city traffic with AI analytics.</p>
        </div>
    """)

# ══════════════════════════════════════════════════════════════
#  ENCODING MAPS  (unchanged from original)
# ══════════════════════════════════════════════════════════════
CITY_MAP    = {"Jaipur": 0, "Patna": 1, "Samastipur": 2}
WEATHER_MAP = {"Clear": 0, "Clouds": 1, "Rain": 2}
ROAD_MAP    = {"Dry": 0, "Wet": 1}
DAY_MAP     = {
    "Monday": 1, "Tuesday": 5, "Wednesday": 6, "Thursday": 4,
    "Friday": 0, "Saturday": 2, "Sunday": 3,
}

def _result_labels(pred: int) -> tuple:
    """Map model output → display tuple. Logic unchanged from original."""
    _m = {
        0: ("LOW",    "low",    25, "#22c55e",
            '<span class="badge-low">LOW</span>',    "25%", "Light Traffic"),
        1: ("MEDIUM", "medium", 60, "#f59e0b",
            '<span class="badge-medium">MEDIUM</span>', "60%", "Moderate Traffic"),
        2: ("HIGH",   "high",   90, "#ef4444",
            '<span class="badge-high">HIGH</span>',  "90%", "Heavy Traffic"),
    }
    return _m[int(pred)]

# ══════════════════════════════════════════════════════════════
#  FIX 3: RESULT CARD RENDERER
#  HTML built as a flat concatenated string — ZERO indentation
#  inside the string itself, so Streamlit's Markdown parser
#  never interprets it as a fenced code block.
# ══════════════════════════════════════════════════════════════
def _result_card() -> None:
    tc   = st.session_state.traffic_class
    tt   = st.session_state.traffic_text
    ts   = st.session_state.status_text
    cb   = st.session_state.congestion_badge
    prob = st.session_state.probability

    # One flat string — Markdown cannot treat this as a code block
    st.markdown(
        '<div class="result-content">'
          '<div class="left-result">'
            '<div class="traffic-wrapper">'
              '<div class="ring"></div>'
              '<span class="car-icon">🚗</span>'
            '</div>'
            f'<h1 class="traffic-level {tc}">{tt}</h1>'
            f'<p class="traffic-status">{ts}</p>'
          '</div>'
          '<div class="traffic-info">'
            '<div class="info-box"><h4>Congestion</h4>' + cb + '</div>'
            f'<div class="info-box"><h4>Probability</h4><span>{prob}</span></div>'
            f'<div class="info-box"><h4>Status</h4><span>{ts}</span></div>'
          '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.traffic_value > 0:
        g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.traffic_value,
            title={"text": ts, "font": {"color": "white", "size": 13}},
            gauge={
                "axis":        {"range": [None, 100], "tickcolor": "white"},
                "bar":         {"color": st.session_state.traffic_color},
                "steps": [
                    {"range": [0,  40], "color": "rgba(34,197,94,0.12)"},
                    {"range": [40, 70], "color": "rgba(250,204,21,0.12)"},
                    {"range": [70,100], "color": "rgba(255,59,59,0.12)"},
                ],
                "bgcolor":     "rgba(0,0,0,0)",
                "bordercolor": "#243041",
            },
        ))
        g.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "white"},
            height=195,
            margin=dict(l=10, r=10, t=28, b=10),
        )
        st.plotly_chart(g, use_container_width=True, key="gauge")

# ══════════════════════════════════════════════════════════════
#  FIX 7: PREDICT CARD
#  All inputs wired correctly; key suffix prevents widget-key
#  collisions when the card is reused on multiple pages.
# ══════════════════════════════════════════════════════════════
def _predict_card(sfx: str) -> None:
    with st.container(border=True):
        html('<p class="card-title">🔮 Predict Traffic</p>')
        html('<p class="card-subtitle">Fill in the details below and hit Predict.</p>')

        lc, rc = st.columns(2, gap="small")
        with lc:
            city    = st.selectbox("Select City",     list(CITY_MAP),    key=f"city_{sfx}")
            day     = st.selectbox("Select Day",      list(DAY_MAP),     key=f"day_{sfx}")
            weather = st.selectbox("Weather",         list(WEATHER_MAP), key=f"wx_{sfx}")
            road    = st.selectbox("Road Condition",  list(ROAD_MAP),    key=f"road_{sfx}")
        with rc:
            hour = st.slider("Hour",            0,  23,  10, key=f"hr_{sfx}")
            vc   = st.slider("Vehicle Count",   0, 500, 200, key=f"vc_{sfx}")
            spd  = st.slider("Avg Speed (km/h)",0, 120,  60, key=f"spd_{sfx}")

        if st.button("🚀 Predict Traffic", key=f"btn_{sfx}", use_container_width=True):
            try:
                inp = pd.DataFrame(
                    [[CITY_MAP[city], hour, DAY_MAP[day],
                      WEATHER_MAP[weather], ROAD_MAP[road], vc, spd]],
                    columns=["city","hour","day","weather_main",
                             "road_condition","vehicle_count","avg_speed"],
                )
                pred = model.predict(inp)[0]
                tt, tc, tv, color, cb, prob, stat = _result_labels(pred)
                st.session_state.update(
                    traffic_text=tt, traffic_class=tc, traffic_value=tv,
                    traffic_color=color, congestion_badge=cb,
                    probability=prob, status_text=stat,
                )
                st.session_state.history.append({
                    "City": city, "Day": day, "Weather": weather,
                    "Road": road, "Hour": hour,
                    "Vehicles": vc, "Speed": f"{spd} km/h",
                    "Traffic": tt,
                    "Time": datetime.now().strftime("%H:%M:%S"),
                })
            except Exception as _e:
                st.error(f"Prediction error: {_e}")

# ══════════════════════════════════════════════════════════════
#  SHARED CHART THEME
# ══════════════════════════════════════════════════════════════
def _theme(fig, h: int = 220):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="white", margin=dict(l=0, r=0, t=10, b=0), height=h,
    )
    fig.update_xaxes(color="#9CA3AF", gridcolor="#243041", zeroline=False)
    fig.update_yaxes(color="#9CA3AF", gridcolor="#243041", zeroline=False)
    return fig

def _section(title: str, sub: str = "") -> None:
    st.markdown(f"<h2 class='page-title'>{title}</h2>", unsafe_allow_html=True)
    if sub:
        st.markdown(f"<p class='page-sub'>{sub}</p>", unsafe_allow_html=True)

_HOURLY = [25,40,55,62,70,82,90,85,76,65,58,62,70,80,88,92,85,78,72,65,55,48,35,28]

# ══════════════════════════════════════════════════════════════
#  PAGE ROUTER  — all 9 pages implemented
# ══════════════════════════════════════════════════════════════

# ── 0: DASHBOARD ────────────────────────────────────────────
if page == NAV_PAGES[0]:

    c1, c2 = st.columns([1.1, 0.9], gap="medium")
    with c1:
        _predict_card("dash")
    with c2:
        with st.container(border=True):
            html('<p class="card-title">📊 Traffic Level</p>')
            _result_card()

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3, gap="medium")

    with b1:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;text-align:center;"
                        "margin-bottom:8px'>📉 Traffic by Hour</h3>",
                        unsafe_allow_html=True)
            fig = _theme(px.line(
                pd.DataFrame({"Hour": list(range(24)), "Traffic": _HOURLY}),
                x="Hour", y="Traffic", color_discrete_sequence=["#6D5DFB"],
            ))
            st.plotly_chart(fig, use_container_width=True)

    with b2:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;text-align:center;"
                        "margin-bottom:8px'>🥧 Day-Type Split</h3>",
                        unsafe_allow_html=True)
            fig = px.pie(
                pd.DataFrame({"Type":["Weekday","Weekend","Holiday"],"Traffic":[75,45,30]}),
                values="Traffic", names="Type", hole=0.5,
                color_discrete_sequence=["#6D5DFB","#22c55e","#facc15"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                margin=dict(l=0,r=0,t=10,b=0), height=220,
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig, use_container_width=True)

    with b3:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;text-align:center;"
                        "margin-bottom:8px'>🌦️ Weather Impact</h3>",
                        unsafe_allow_html=True)
            fig = _theme(px.bar(
                pd.DataFrame({"Weather":["Clear","Clouds","Rain"],"Congestion":[42,65,88]}),
                x="Weather", y="Congestion", color_discrete_sequence=["#6D5DFB"],
            ))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<h3 style='color:white;font-size:15px;margin-bottom:10px'>"
                    "📝 Recent Predictions</h3>", unsafe_allow_html=True)
        if st.session_state.history:
            st.dataframe(pd.DataFrame(st.session_state.history),
                         use_container_width=True, hide_index=True)
        else:
            st.markdown("<p style='color:#9CA3AF;font-size:13px'>"
                        "No predictions yet — use the Predict Traffic form above.</p>",
                        unsafe_allow_html=True)

# ── 1: PREDICTION ───────────────────────────────────────────
elif page == NAV_PAGES[1]:
    _section("🔮 Prediction", "Run a detailed traffic forecast for any city and time.")
    p1, p2 = st.columns([1.1, 0.9], gap="medium")
    with p1:
        _predict_card("pred")
    with p2:
        with st.container(border=True):
            html('<p class="card-title">📊 Traffic Level</p>')
            _result_card()

# ── 2: ANALYTICS ────────────────────────────────────────────
elif page == NAV_PAGES[2]:
    _section("📈 Analytics", "Traffic trend analysis across hours, days, and weather.")

    a1, a2 = st.columns(2, gap="medium")
    with a1:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;margin-bottom:6px'>"
                        "📉 Hourly Traffic Volume</h3>", unsafe_allow_html=True)
            fig = _theme(px.area(
                pd.DataFrame({"Hour": list(range(24)), "Traffic": _HOURLY}),
                x="Hour", y="Traffic", color_discrete_sequence=["#6D5DFB"],
            ), h=270)
            st.plotly_chart(fig, use_container_width=True)

    with a2:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;margin-bottom:6px'>"
                        "📅 Day-of-Week Pattern</h3>", unsafe_allow_html=True)
            fig = _theme(px.bar(
                pd.DataFrame({"Day":["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                              "Traffic":[72,68,75,80,88,55,42]}),
                x="Day", y="Traffic", color_discrete_sequence=["#6D5DFB"],
            ), h=270)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    a3, a4 = st.columns(2, gap="medium")

    with a3:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;margin-bottom:6px'>"
                        "🌦️ Weather vs Congestion</h3>", unsafe_allow_html=True)
            wdf = pd.DataFrame({
                "Weather":    ["Clear","Clouds","Rain"],
                "Congestion": [42,65,88],
                "C":          ["#22c55e","#facc15","#ff6b6b"],
            })
            fig = _theme(px.bar(wdf, x="Weather", y="Congestion", color="C",
                color_discrete_map={"#22c55e":"#22c55e","#facc15":"#facc15","#ff6b6b":"#ff6b6b"}
            ), h=260)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    with a4:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;margin-bottom:6px'>"
                        "🥧 Level Distribution</h3>", unsafe_allow_html=True)
            fig = px.pie(
                pd.DataFrame({"Level":["Low","Medium","High"],"Count":[40,35,25]}),
                values="Count", names="Level", hole=0.55,
                color_discrete_sequence=["#22c55e","#facc15","#ff6b6b"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                height=260, margin=dict(l=0,r=0,t=10,b=0),
                legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<h3 style='color:white;font-size:14px;margin-bottom:6px'>"
                    "🏙️ City Comparison</h3>", unsafe_allow_html=True)
        city_comp = pd.DataFrame({
            "City":  ["Jaipur"]*3 + ["Patna"]*3 + ["Samastipur"]*3,
            "Level": ["Low","Medium","High"]*3,
            "Count": [45,30,25, 30,40,30, 50,30,20],
        })
        fig = _theme(px.bar(
            city_comp, x="City", y="Count", color="Level", barmode="group",
            color_discrete_map={"Low":"#22c55e","Medium":"#facc15","High":"#ff6b6b"},
        ), h=280)
        fig.update_layout(legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

# ── 3: TRAFFIC MAP ──────────────────────────────────────────
elif page == NAV_PAGES[3]:
    _section("📍 Traffic Map", "Live congestion overview across monitored cities.")

    cities = pd.DataFrame({
        "City":     ["Jaipur",  "Patna",   "Samastipur"],
        "lat":      [26.9124,   25.5941,    25.8700],
        "lon":      [75.7873,   85.1376,    85.7800],
        "Status":   ["Moderate","Heavy",   "Light"],
        "Level":    [60,        90,         25],
        "Vehicles": [320,       450,        180],
    })
    # Reflect latest prediction for the matching city
    if st.session_state.traffic_value > 0:
        last_city = next(
            (h["City"] for h in reversed(st.session_state.history) if "City" in h),
            None,
        )
        if last_city:
            mask = cities["City"] == last_city
            cities.loc[mask, "Level"]  = st.session_state.traffic_value
            cities.loc[mask, "Status"] = st.session_state.status_text

    col_map, col_info = st.columns([2, 1], gap="medium")

    with col_map:
        with st.container(border=True):
            try:
                fig_map = px.scatter_mapbox(
                    cities, lat="lat", lon="lon",
                    hover_name="City",
                    hover_data={"Status":True,"Vehicles":True,
                                "Level":False,"lat":False,"lon":False},
                    size="Level", color="Status",
                    color_discrete_map={
                        "Light":"#22c55e","Moderate":"#facc15","Heavy":"#ff6b6b",
                        "Light Traffic":"#22c55e","Moderate Traffic":"#facc15",
                        "Heavy Traffic":"#ff6b6b",
                    },
                    zoom=4.5, center={"lat":26.2,"lon":82.0},
                    mapbox_style="open-street-map", size_max=40, height=460,
                )
                fig_map.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0,r=0,t=0,b=0),
                    legend=dict(font=dict(color="white"), bgcolor="rgba(20,30,48,0.8)"),
                )
                st.plotly_chart(fig_map, use_container_width=True)
            except Exception:
                # Fallback scatter when mapbox tiles unavailable
                fig_fb = _theme(px.scatter(
                    cities, x="lon", y="lat", size="Level", color="Status",
                    hover_name="City", text="City",
                    color_discrete_map={"Light":"#22c55e","Moderate":"#facc15","Heavy":"#ff6b6b"},
                    size_max=40,
                ), h=420)
                fig_fb.update_traces(textposition="top center")
                st.plotly_chart(fig_fb, use_container_width=True)

    with col_info:
        _color_map = {
            "Light":"#22c55e","Moderate":"#facc15","Heavy":"#ff6b6b",
            "Light Traffic":"#22c55e","Moderate Traffic":"#facc15",
            "Heavy Traffic":"#ff6b6b",
        }
        for _, row in cities.iterrows():
            c = _color_map.get(str(row["Status"]), "#9CA3AF")
            html(f"""
            <div style="background:rgba(255,255,255,0.05);
                        border:1px solid #243041;border-left:4px solid {c};
                        border-radius:12px;padding:14px 16px;margin-bottom:12px;">
                <h4 style="color:white;margin:0 0 5px;font-size:15px;">📍 {row['City']}</h4>
                <p style="color:{c};margin:0 0 3px;font-size:13px;font-weight:600;">{row['Status']}</p>
                <p style="color:#9CA3AF;margin:0;font-size:12px;">
                    {row['Vehicles']} vehicles &nbsp;·&nbsp; Intensity {row['Level']}%
                </p>
            </div>
            """)

# ── 4: HISTORY ──────────────────────────────────────────────
elif page == NAV_PAGES[4]:
    _section("📜 Prediction History", "All predictions made in this session.")

    with st.container(border=True):
        if st.session_state.history:
            df_h = pd.DataFrame(st.session_state.history)
            st.dataframe(df_h, use_container_width=True, hide_index=True)
            hc1, hc2 = st.columns(2)
            with hc1:
                if st.button("🗑️ Clear History", key="clr_hist"):
                    st.session_state.history = []
                    st.rerun()
            with hc2:
                csv = df_h.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Export CSV", csv,
                                   "traffic_history.csv", "text/csv",
                                   key="dl_hist")
        else:
            st.markdown("<p style='color:#9CA3AF;padding:20px 0'>"
                        "No predictions yet. Head to Dashboard or Prediction.</p>",
                        unsafe_allow_html=True)

# ── 5: ALERTS ───────────────────────────────────────────────
elif page == NAV_PAGES[5]:
    _section("🔔 Traffic Alerts", "Live alerts and traffic notifications.")

    _alerts = [
        ("high",  "Jaipur",    "Peak hour congestion on MI Road — expect 25 min delay",        "3 min ago",  "🔴"),
        ("medium","Patna",     "Moderate traffic near Patna Junction due to ongoing event",     "11 min ago", "🟡"),
        ("low",   "Samastipur","Roads cleared after earlier incident — normal flow resumed",    "22 min ago", "🟢"),
        ("high",  "Jaipur",    "Heavy rain causing slippery roads — reduce speed on NH-48",     "34 min ago", "🔴"),
        ("medium","Samastipur","Construction detour active on Station Road until 17:00",        "1 hr ago",   "🟡"),
        ("low",   "Patna",     "Light traffic expected throughout the evening on all routes",   "1 hr ago",   "🟢"),
    ]

    al_col1, al_col2 = st.columns([3, 1], gap="medium")
    with al_col1:
        with st.container(border=True):
            for sev, city, msg, age, icon in _alerts:
                _c = {"high":"#ff6b6b","medium":"#facc15","low":"#22c55e"}[sev]
                html(f"""
                <div class="alert-card {sev}">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                        <span class="a-type" style="color:{_c}">{icon} {sev.upper()}</span>
                        <span style="color:#6B7280;font-size:11px">{age}</span>
                    </div>
                    <p class="a-msg">{msg}</p>
                    <p class="a-meta">📍 {city}</p>
                </div>
                """)

    with al_col2:
        with st.container(border=True):
            html('<p class="card-title">Summary</p>')
            hi  = sum(1 for a in _alerts if a[0]=="high")
            med = sum(1 for a in _alerts if a[0]=="medium")
            lo  = sum(1 for a in _alerts if a[0]=="low")
            html(f"""
            <div style="display:flex;flex-direction:column;gap:12px;margin-top:14px">
                <div class="metric-card" style="border-left:4px solid #ff6b6b">
                    <div class="m-val" style="color:#ff6b6b">{hi}</div>
                    <div class="m-lbl">High Alerts</div>
                </div>
                <div class="metric-card" style="border-left:4px solid #facc15">
                    <div class="m-val" style="color:#facc15">{med}</div>
                    <div class="m-lbl">Medium Alerts</div>
                </div>
                <div class="metric-card" style="border-left:4px solid #22c55e">
                    <div class="m-val" style="color:#22c55e">{lo}</div>
                    <div class="m-lbl">Low Alerts</div>
                </div>
            </div>
            """)

# ── 6: REPORTS ──────────────────────────────────────────────
elif page == NAV_PAGES[6]:
    _section("📊 Reports", "Session statistics and prediction log.")

    hist    = st.session_state.history
    total   = len(hist)
    hi_n    = sum(1 for h in hist if h.get("Traffic")=="HIGH")
    med_n   = sum(1 for h in hist if h.get("Traffic")=="MEDIUM")
    lo_n    = sum(1 for h in hist if h.get("Traffic")=="LOW")

    r1, r2, r3, r4 = st.columns(4, gap="medium")
    for col, (lbl, val, icon, color) in zip(
        [r1, r2, r3, r4],
        [("Total Runs", total, "🔢","white"),
         ("High",       hi_n,  "🔴","#ff6b6b"),
         ("Moderate",   med_n, "🟡","#facc15"),
         ("Light",      lo_n,  "🟢","#22c55e")],
    ):
        with col:
            html(f"""
            <div class="metric-card">
                <div style="font-size:26px">{icon}</div>
                <div class="m-val" style="color:{color}">{val}</div>
                <div class="m-lbl">{lbl}</div>
            </div>
            """)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    rc1, rc2 = st.columns([1.5, 1], gap="medium")

    with rc1:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;margin-bottom:6px'>"
                        "Prediction Breakdown</h3>", unsafe_allow_html=True)
            if hist:
                # pandas 2.0+: value_counts().reset_index() gives ["Traffic","count"]
                # Build explicitly to be version-agnostic
                _vc = pd.DataFrame(hist)["Traffic"].value_counts()
                cnt = pd.DataFrame({"Traffic": _vc.index.tolist(),
                                    "Count":   _vc.values.tolist()})
                fig = _theme(px.bar(cnt, x="Traffic", y="Count",
                    color="Traffic",
                    color_discrete_map={"HIGH":"#ff6b6b","MEDIUM":"#facc15","LOW":"#22c55e"}
                ), h=260)
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown("<p style='color:#9CA3AF;padding:20px 0'>"
                            "No data yet — run some predictions first.</p>",
                            unsafe_allow_html=True)

    with rc2:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;margin-bottom:6px'>"
                        "City Distribution</h3>", unsafe_allow_html=True)
            if hist:
                # pandas 2.0+: build from Series explicitly — version-agnostic
                _cvc = pd.DataFrame(hist)["City"].value_counts()
                cc = pd.DataFrame({"City":  _cvc.index.tolist(),
                                   "Count": _cvc.values.tolist()})
                fig2 = px.pie(cc, values="Count", names="City", hole=0.5,
                    color_discrete_sequence=["#6D5DFB","#22c55e","#facc15"])
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", font_color="white",
                    height=260, margin=dict(l=0,r=0,t=10,b=0),
                    legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)"),
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.markdown("<p style='color:#9CA3AF;padding:20px 0'>No data yet.</p>",
                            unsafe_allow_html=True)

    if hist:
        st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;margin-bottom:10px'>"
                        "Full Prediction Log</h3>", unsafe_allow_html=True)
            df_rep = pd.DataFrame(hist)
            st.dataframe(df_rep, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Download Report (CSV)",
                df_rep.to_csv(index=False).encode("utf-8"),
                "traffic_report.csv", "text/csv", key="dl_rep",
            )

# ── 7: SETTINGS ─────────────────────────────────────────────
elif page == NAV_PAGES[7]:
    _section("⚙ Settings", "Configure app preferences and defaults.")

    s1, s2 = st.columns(2, gap="medium")
    with s1:
        with st.container(border=True):
            html('<p class="card-title">General Preferences</p>')
            new_city = st.selectbox(
                "Default City", list(CITY_MAP),
                index=list(CITY_MAP).index(st.session_state.pref_city),
                key="set_city",
            )
            st.session_state.pref_city = new_city

            notify  = st.toggle("Enable Alert Notifications",
                                value=st.session_state.pref_notify, key="set_notify")
            compact = st.toggle("Compact Layout",
                                value=st.session_state.pref_compact, key="set_compact")
            st.session_state.pref_notify  = notify
            st.session_state.pref_compact = compact

            st.markdown("<hr style='border-color:#243041;margin:16px 0'>",
                        unsafe_allow_html=True)
            if st.button("Reset to Defaults", key="reset_prefs"):
                st.session_state.pref_city    = "Jaipur"
                st.session_state.pref_notify  = True
                st.session_state.pref_compact = False
                st.success("Settings reset to defaults.")

    with s2:
        with st.container(border=True):
            html('<p class="card-title">Data & Session</p>')
            st.markdown(
                "<p style='color:#9CA3AF;font-size:13px;margin-bottom:16px'>"
                "Session data is held in memory only and cleared when the tab closes.</p>",
                unsafe_allow_html=True,
            )
            pred_count = len(st.session_state.history)
            html(f"""
            <div class="metric-card" style="margin-bottom:14px">
                <div class="m-val">{pred_count}</div>
                <div class="m-lbl">Predictions this session</div>
            </div>
            """)
            if st.button("🗑️ Clear All Session Data", key="clr_all"):
                for _k2 in ["traffic_text","traffic_class","traffic_value",
                             "traffic_color","congestion_badge","probability",
                             "status_text","history"]:
                    st.session_state[_k2] = _DEFAULTS[_k2]
                st.success("Session data cleared.")
                st.rerun()

        st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            html('<p class="card-title">Model Info</p>')
            html("""
            <div style="color:#9CA3AF;font-size:13px;line-height:1.8;margin-top:10px">
                <p><span style="color:white;font-weight:600">File:</span> traffic_model.pkl</p>
                <p><span style="color:white;font-weight:600">Features:</span>
                   City · Hour · Day · Weather · Road · Vehicles · Speed</p>
                <p><span style="color:white;font-weight:600">Output:</span>
                   Low / Medium / High congestion class</p>
            </div>
            """)

# ── 8: ABOUT ────────────────────────────────────────────────
elif page == NAV_PAGES[8]:
    _section("ℹ About", "Smart Traffic Prediction System — built with AI and Streamlit.")

    ab1, ab2 = st.columns([1.5, 1], gap="medium")
    with ab1:
        with st.container(border=True):
            html("""
            <h2 style="color:white;font-size:20px;margin-bottom:10px">🚗 Traffic Prediction System</h2>
            <p style="color:#9CA3AF;font-size:14px;line-height:1.8;margin-bottom:16px">
                A machine-learning powered dashboard for real-time traffic congestion
                prediction across Jaipur, Patna, and Samastipur.  Input local conditions
                and get an instant Low / Medium / High classification with a live gauge.
            </p>
            <h4 style="color:white;font-size:14px;margin-bottom:8px">How it works</h4>
            <ol style="color:#9CA3AF;font-size:13px;padding-left:18px;line-height:2">
                <li>Select city, day, weather, and road conditions.</li>
                <li>Set the hour, vehicle count, and average speed.</li>
                <li>Click <strong style="color:white">Predict Traffic</strong> — the model classifies congestion.</li>
                <li>View the animated result ring and gauge chart.</li>
                <li>Check Analytics and Reports for trends over your session.</li>
            </ol>
            """)

    with ab2:
        with st.container(border=True):
            html('<p class="card-title">Tech Stack</p>')
            _stack = [
                ("🐍","Python 3.x",    "Core language"),
                ("⚡","Streamlit",     "Web framework"),
                ("🧠","scikit-learn",  "ML model"),
                ("🐼","Pandas",        "Data manipulation"),
                ("📊","Plotly",        "Interactive charts"),
                ("🔧","joblib",        "Model serialisation"),
            ]
            for ico, name, desc in _stack:
                html(f"""
                <div style="display:flex;align-items:center;gap:12px;
                            background:rgba(255,255,255,0.04);
                            border:1px solid #243041;border-radius:10px;
                            padding:10px 14px;margin-bottom:8px">
                    <span style="font-size:20px">{ico}</span>
                    <div>
                        <div style="color:white;font-size:13px;font-weight:600">{name}</div>
                        <div style="color:#9CA3AF;font-size:11px">{desc}</div>
                    </div>
                </div>
                """)

        st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            html("""
            <p class="card-title">Changelog</p>
            <div style="color:#9CA3AF;font-size:13px;margin-top:10px;line-height:2">
                <p>v4.0 — All 9 pages, live clock fragment, icon fix, sidebar gap</p>
                <p>v3.0 — Full page routing, st.radio nav, result card fix</p>
                <p>v2.0 — UI/UX polish, analytics, gauge chart</p>
                <p>v1.0 — Initial ML integration</p>
            </div>
            """)

# ══════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════
html("""
<div style="text-align:center;color:#9CA3AF;font-size:12px;
            margin:32px 0 16px;padding-top:16px;border-top:1px solid #243041">
    🚦 Smart Traffic Prediction System &nbsp;|&nbsp;
    AI + Machine Learning + Streamlit
</div>
""")
