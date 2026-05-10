import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import textwrap

# ── Helper: strips Python indentation so HTML never triggers Markdown code-blocks
def html(s: str):
    st.markdown(textwrap.dedent(s).strip(), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Traffic Prediction System",
    page_icon="🚦",
    layout="wide"
)

# ════════════════════════════════════════════════════════════
#  LOAD MODEL
# ════════════════════════════════════════════════════════════
try:
    model = joblib.load("traffic_model.pkl")
except Exception as e:
    st.error(f"⚠️ Model load failed: {e}")
    st.stop()

# ════════════════════════════════════════════════════════════
#  FULL CSS  — all 5 bug-fixes baked in
# ════════════════════════════════════════════════════════════
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
      rel="stylesheet"/>

<style>

/* ── 1. HIDE STREAMLIT CHROME ─────────────────────────────── */
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }
[data-testid="collapsedControl"]                  { display: none !important; }

/* ── 2. GLOBAL ────────────────────────────────────────────── */
*, *::before, *::after {
    font-family: 'Poppins', sans-serif !important;
    box-sizing: border-box;
}
body { background-color: #070F1F !important; margin: 0; padding: 0; }
.stApp, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0b132b 0%, #1c2541 50%, #3a506b 100%) !important;
}

/* ── 3. MAIN CONTENT PADDING (fixes sidebar-attached bug) ─── */
.block-container {
    padding: 0 1.5rem 2rem 1.5rem !important;
    max-width: 100% !important;
}
[data-testid="stMain"] { padding-top: 0 !important; }

/* ── 4. NAVBAR ────────────────────────────────────────────── */
#navbar {
    height: 70px;
    display: flex;
    align-items: center;
    padding: 0 24px;
    background-color: #0f1937;
    color: white;
    position: sticky;
    top: 0;
    z-index: 999;
    width: 100%;
    margin-bottom: 20px;
}
#logo            { display: flex; align-items: center; gap: 12px; }
#logo-text       { display: flex; flex-direction: column; }
#logo h1         { font-size: 19px; margin: 0; color: white !important; font-weight: 600; }
#logo p          { font-size: 11px; color: #9CA3AF; margin: 0; }
#logo-icon       { font-size: 26px; }
#nav-right       { display: flex; align-items: center; gap: 16px; margin-left: auto; }
.nav-pill {
    background: rgba(255,255,255,0.05);
    border: 1px solid #243041;
    border-radius: 100px;
    padding: 7px 14px;
    font-size: 13px;
    font-weight: 500;
    color: white;
    transition: border-color 0.3s, box-shadow 0.3s;
    white-space: nowrap;
}
.nav-pill:hover {
    border-color: rgba(59,130,246,0.4);
    box-shadow: 0 0 8px rgba(59,130,246,0.2);
}

/* ── 5. SIDEBAR ───────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #141E30, #243B55) !important;
    border-right: 1px solid #243041 !important;
    min-width: 240px !important;
    max-width: 240px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 12px 12px 20px 12px !important;
}

/* ── 6. SIDEBAR RADIO → NAV ITEMS ────────────────────────── */
/*  BUG FIX: use st.radio styled with CSS instead of HTML divs.
    Real Python callbacks, active-state via CSS :has(), and
    NO transform/translateX so sidebar never collapses or
    double-paints on hover.                                    */
[data-testid="stSidebar"] [data-testid="stRadio"] {
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 10px 14px !important;
    border-radius: 14px !important;
    color: rgba(255,255,255,0.85) !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: background 0.2s ease, color 0.2s ease !important;
    user-select: none !important;
    /* NO transform — avoids double-paint & sidebar collapse */
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.09) !important;
    color: white !important;
}
/* Hide the radio circle bullet */
[data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child,
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radio"] {
    display: none !important;
}
/* Active item - :has() supported Chrome 105+, FF 121+, Safari 15.4+ */
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #6D5DFB !important;
    color: white !important;
}

/* Side info card */
#side-card {
    margin-top: 18px;
    background: rgba(255,255,255,0.05);
    border: 1px solid #243041;
    border-radius: 18px;
    padding: 14px;
    text-align: center;
    transition: border-color 0.3s, box-shadow 0.3s;
}
#side-card:hover {
    border-color: rgba(109,93,251,0.5);
    box-shadow: 0 0 12px rgba(109,93,251,0.2);
}
#side-card h4 { color: white !important; margin: 6px 0 3px; font-size: 13px; }
#side-card p  { color: #9CA3AF !important; font-size: 11px; margin: 0; }

/* ── 7. CARD CONTAINERS ───────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid #243041 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    transition: border-color 0.3s, box-shadow 0.3s, transform 0.3s !important;
    padding: 14px !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(59,130,246,0.4) !important;
    box-shadow: 0 0 18px rgba(59,130,246,0.2), 0 0 40px rgba(95,196,28,0.1) !important;
    transform: translateY(-4px) !important;
}
.card-title    { font-size: 19px; font-weight: 600; color: white !important; margin: 0 0 3px 0; }
.card-subtitle { font-size: 12px; color: #9CA3AF; margin: 0 0 16px 0; }

/* ── 8. INPUT WIDGETS ─────────────────────────────────────── */
.stSelectbox label, .stSlider label {
    color: #9CA3AF !important;
    font-size: 13px !important;
    font-weight: 400 !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.08) !important;
    color: white !important;
    border: 1px solid #243041 !important;
    border-radius: 10px !important;
}
[data-testid="stSelectbox"] svg { fill: #9CA3AF !important; }
.stSlider [role="slider"] { background-color: #6D5DFB !important; }
[data-baseweb="slider"] div[data-baseweb="slider-track-fill"] { background: #6D5DFB !important; }

/* ── 9. PREDICT BUTTON ────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #6D5DFB, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 13px 24px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    width: 100% !important;
    margin-top: 12px !important;
    letter-spacing: 0.5px !important;
    transition: box-shadow 0.3s ease !important;
}
.stButton > button:hover {
    box-shadow: 0 0 22px rgba(109,93,251,0.55) !important;
}

/* ── 10. RESULT CARD ──────────────────────────────────────── */
.result-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    margin-top: 12px;
    flex-wrap: wrap;
}
.left-result { display: flex; flex-direction: column; align-items: center; }
.traffic-wrapper {
    position: relative;
    width: 105px;
    height: 105px;
    flex-shrink: 0;
}
.ring {
    width: 105px; height: 105px;
    border-radius: 50%;
    background: conic-gradient(#22c55e, #facc15, #ff7b00, #ff3b3b, #22c55e);
    animation: rotateRing 6s linear infinite;
}
.ring::before {
    content: "";
    position: absolute;
    inset: 10px;
    border-radius: 50%;
    background: #2c3858;
}
.car-icon {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 26px;
    z-index: 5;
    animation: floatCar 2s ease-in-out infinite;
}
.traffic-level {
    font-size: 30px; letter-spacing: 2px; font-weight: 700;
    margin-top: 10px; text-align: center;
}
.traffic-level.awaiting { color: #6B7280; }
.traffic-level.low {
    background: linear-gradient(90deg,#22c55e,#16a34a);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.traffic-level.medium {
    background: linear-gradient(90deg,#facc15,#f59e0b,#ff7b00);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.traffic-level.high {
    background: linear-gradient(90deg,#ffb800,#ff7b00,#ff3b3b);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.traffic-status { color: #AEB6C8; font-size: 13px; margin-top: -4px; }
.traffic-info { display: flex; flex-direction: column; gap: 10px; }
.info-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 10px 14px;
    min-width: 120px;
    transition: border-color 0.3s, transform 0.3s;
}
.info-box:hover { border-color: rgba(109,93,251,0.45); transform: translateY(-4px); }
.info-box h4   { font-size: 11px; color: #9CA3AF; margin: 0 0 4px 0; }
.info-box span { color: white; font-size: 16px; font-weight: 600; }
.badge-high   { color:#ff6b6b!important; background:rgba(193,43,43,0.25);
                border-radius:8px; border:1px solid rgba(255,144,144,0.2);
                padding:3px 9px; font-size:0.82rem; font-weight:700; }
.badge-medium { color:#facc15!important; background:rgba(234,179,8,0.2);
                border-radius:8px; border:1px solid rgba(234,179,8,0.3);
                padding:3px 9px; font-size:0.82rem; font-weight:700; }
.badge-low    { color:#22c55e!important; background:rgba(34,197,94,0.2);
                border-radius:8px; border:1px solid rgba(34,197,94,0.3);
                padding:3px 9px; font-size:0.82rem; font-weight:700; }

/* ── 11. PLOTLY / DATAFRAME / MISC ───────────────────────── */
.js-plotly-plot, .plot-container { background: transparent !important; }
[data-testid="stDataFrameResizable"] { border-radius: 12px !important; overflow: hidden; }
.stDataFrame th { background: #1c2541 !important; color: white !important; }
.stDataFrame td { color: #d1d5db !important; }
[data-testid="stDivider"] hr { border-color: #243041 !important; }
[data-testid="column"]        { padding: 0 6px !important; }
.section-gap                  { margin-top: 20px; }
.coming-soon {
    text-align: center; color: #9CA3AF;
    padding: 80px 20px; font-size: 52px;
}
.coming-soon p { font-size: 15px; margin-top: 8px; }

/* ── 12. ANIMATIONS ───────────────────────────────────────── */
@keyframes rotateRing { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
@keyframes floatCar {
    0%  { transform:translate(-50%,-50%); }
    50% { transform:translate(-50%,-62%); }
    100%{ transform:translate(-50%,-50%); }
}

</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  SESSION STATE — initialise once
# ════════════════════════════════════════════════════════════
_defaults = {
    "traffic_text":     "——",
    "traffic_class":    "awaiting",
    "traffic_value":    0,
    "traffic_color":    "#6B7280",
    "congestion_badge": '<span style="color:#9CA3AF;font-size:14px;">Awaiting</span>',
    "probability":      "—",
    "status_text":      "Run a prediction",
    "history":          [],
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ════════════════════════════════════════════════════════════
#  NAVBAR  — emoji icons, no CDN required
# ════════════════════════════════════════════════════════════
_time = datetime.now().strftime("%I:%M %p")
_date = datetime.now().strftime("%d %b %Y")

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
        <span class="nav-pill">🌤️ 28 °C</span>
        <span class="nav-pill">📅 {_date}</span>
        <span class="nav-pill">🕒 {_time}</span>
    </div>
</div>
""")

# ════════════════════════════════════════════════════════════
#  SIDEBAR — st.radio styled as nav items
#  FIX: real Streamlit widget → actual Python callbacks on
#       click; active state via CSS :has(); NO transform on
#       hover → no text-doubling, no sidebar collapse.
# ════════════════════════════════════════════════════════════
NAV_PAGES = [
    "🏠  Dashboard",
    "📊  Prediction",
    "📈  Analytics",
    "📍  Traffic Map",
    "🕑  History",
    "🔔  Alerts",
    "📋  Reports",
    "⚙️  Settings",
    "ℹ️   About",
]

with st.sidebar:
    page = st.radio(
        "Navigation",
        NAV_PAGES,
        label_visibility="collapsed",
        key="sidebar_nav"
    )
    html("""
        <div id="side-card">
            <div style="font-size:28px;">🤖</div>
            <h4>Smart Traffic AI</h4>
            <p>Predict city traffic with AI analytics.</p>
        </div>
    """)

# ════════════════════════════════════════════════════════════
#  SHARED ENCODING MAPS  (unchanged from original)
# ════════════════════════════════════════════════════════════
CITY_MAP    = {"Jaipur": 0, "Patna": 1, "Samastipur": 2}
WEATHER_MAP = {"Clear": 0, "Clouds": 1, "Rain": 2}
ROAD_MAP    = {"Dry": 0, "Wet": 1}
DAY_MAP     = {"Monday":1,"Tuesday":5,"Wednesday":6,"Thursday":4,
               "Friday":0,"Saturday":2,"Sunday":3}

def _result_labels(pred):
    """Map prediction output to display values — logic unchanged."""
    mapping = {
        0: ("LOW",    "low",    25, "green",  '<span class="badge-low">LOW</span>',    "25 %", "Light Traffic"),
        1: ("MEDIUM", "medium", 60, "orange", '<span class="badge-medium">MEDIUM</span>', "60 %", "Moderate Traffic"),
        2: ("HIGH",   "high",   90, "red",    '<span class="badge-high">HIGH</span>',  "90 %", "Heavy Traffic"),
    }
    return mapping[int(pred)]

def _render_result_card():
    """Renders the Traffic Level card from session_state."""
    _tc   = st.session_state.traffic_class
    _tt   = st.session_state.traffic_text
    _ts   = st.session_state.status_text
    _cb   = st.session_state.congestion_badge
    _prob = st.session_state.probability
    # Flat string — zero indentation inside so Markdown never makes a code block
    st.markdown(
        '<div class="result-content">'
          '<div class="left-result">'
            '<div class="traffic-wrapper">'
              '<div class="ring"></div>'
              '<span class="car-icon">🚗</span>'
            '</div>'
            f'<h1 class="traffic-level {_tc}">{_tt}</h1>'
            f'<p class="traffic-status">{_ts}</p>'
          '</div>'
          '<div class="traffic-info">'
            '<div class="info-box"><h4>Congestion</h4>'
              f'{_cb}'
            '</div>'
            '<div class="info-box"><h4>Probability</h4>'
              f'<span>{_prob}</span>'
            '</div>'
            '<div class="info-box"><h4>Status</h4>'
              f'<span>{_ts}</span>'
            '</div>'
          '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    if st.session_state.traffic_value > 0:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.traffic_value,
            title={"text": _ts, "font": {"color": "white", "size": 13}},
            gauge={
                "axis": {"range": [None, 100], "tickcolor": "white"},
                "bar":  {"color": st.session_state.traffic_color},
                "steps": [
                    {"range": [0,  40], "color": "rgba(34,197,94,0.12)"},
                    {"range": [40, 70], "color": "rgba(250,204,21,0.12)"},
                    {"range": [70,100], "color": "rgba(255,59,59,0.12)"},
                ],
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "#243041",
            }
        ))
        gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color":"white"},
                            height=195, margin=dict(l=10,r=10,t=28,b=10))
        st.plotly_chart(gauge, use_container_width=True)

def _predict_card(suffix=""):
    """Renders the Predict Traffic input card and runs prediction on click."""
    with st.container(border=True):
        html('<p class="card-title">🔮 Predict Traffic</p>')
        html('<p class="card-subtitle">Fill the details below to get a traffic prediction</p>')

        lc, rc = st.columns(2, gap="small")
        with lc:
            city    = st.selectbox("Select City",      list(CITY_MAP),    key=f"city{suffix}")
            day     = st.selectbox("Select Day",       list(DAY_MAP),     key=f"day{suffix}")
            weather = st.selectbox("Weather",          list(WEATHER_MAP), key=f"weather{suffix}")
            road    = st.selectbox("Road Condition",   list(ROAD_MAP),    key=f"road{suffix}")
        with rc:
            hour  = st.slider("Hour",               0, 23,  10, key=f"hr{suffix}")
            vc    = st.slider("Vehicle Count",      0, 500, 200, key=f"vc{suffix}")
            spd   = st.slider("Average Speed (km/h)",0,120, 60, key=f"spd{suffix}")

        if st.button("🚀 Predict Traffic", key=f"btn{suffix}", use_container_width=True):
            try:
                inp = pd.DataFrame([[
                    CITY_MAP[city], hour, DAY_MAP[day],
                    WEATHER_MAP[weather], ROAD_MAP[road], vc, spd
                ]], columns=['city','hour','day','weather_main',
                             'road_condition','vehicle_count','avg_speed'])
                pred = model.predict(inp)[0]
                tt, tc, tv, color, cb, prob, stat = _result_labels(pred)
                st.session_state.update(
                    traffic_text=tt, traffic_class=tc, traffic_value=tv,
                    traffic_color=color, congestion_badge=cb,
                    probability=prob, status_text=stat
                )
                st.session_state.history.append({
                    "City": city, "Traffic": tt,
                    "Vehicles": vc, "Speed": f"{spd} km/h",
                    "Time": datetime.now().strftime("%H:%M"),
                })
            except Exception as e:
                st.error(f"Prediction error: {e}")

# ════════════════════════════════════════════════════════════
#  PAGE ROUTER
# ════════════════════════════════════════════════════════════

# ─────────────────── DASHBOARD ──────────────────────────────
if page == NAV_PAGES[0]:

    top_col1, top_col2 = st.columns([1.1, 0.9], gap="medium")

    with top_col1:
        _predict_card(suffix="_dash")

    with top_col2:
        with st.container(border=True):
            html('<p class="card-title">📊 Traffic Level</p>')
            _render_result_card()

    # Analytics
    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    b1, b2, b3 = st.columns(3, gap="medium")

    with b1:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;text-align:center;"
                        "margin-bottom:8px;'>📉 Traffic By Hour</h3>",
                        unsafe_allow_html=True)
            tdata=[25,40,55,62,70,82,90,85,76,65,58,62,70,80,88,92,85,78,72,65,55,48,35,28]
            fig1=px.line(pd.DataFrame({"Hour":list(range(24)),"Traffic":tdata}),
                         x="Hour",y="Traffic",color_discrete_sequence=["#6D5DFB"])
            fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                               font_color="white",margin=dict(l=0,r=0,t=5,b=0),height=200)
            fig1.update_xaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            fig1.update_yaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            st.plotly_chart(fig1,use_container_width=True)

    with b2:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;text-align:center;"
                        "margin-bottom:8px;'>🥧 Traffic By Day Type</h3>",
                        unsafe_allow_html=True)
            fig2=px.pie(pd.DataFrame({"Type":["Weekday","Weekend","Holiday"],
                                      "Traffic":[75,45,30]}),
                        values="Traffic",names="Type",hole=0.5,
                        color_discrete_sequence=["#6D5DFB","#22c55e","#facc15"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="white",
                               margin=dict(l=0,r=0,t=5,b=0),height=200,
                               legend=dict(font=dict(color="white"),bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig2,use_container_width=True)

    with b3:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;text-align:center;"
                        "margin-bottom:8px;'>🌦️ Weather Impact</h3>",
                        unsafe_allow_html=True)
            fig3=px.bar(pd.DataFrame({"Weather":["Clear","Clouds","Rain"],
                                      "Congestion":[42,65,88]}),
                        x="Weather",y="Congestion",color_discrete_sequence=["#6D5DFB"])
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                               font_color="white",margin=dict(l=0,r=0,t=5,b=0),height=200)
            fig3.update_xaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            fig3.update_yaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            st.plotly_chart(fig3,use_container_width=True)

    # History
    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("<h3 style='color:white;font-size:15px;margin-bottom:10px;'>"
                    "📝 Recent Predictions</h3>", unsafe_allow_html=True)
        if st.session_state.history:
            st.dataframe(pd.DataFrame(st.session_state.history),
                         use_container_width=True, hide_index=True)
        else:
            st.markdown("<p style='color:#9CA3AF;font-size:13px;'>"
                        "No predictions yet — hit Predict Traffic to begin.</p>",
                        unsafe_allow_html=True)

# ─────────────────── PREDICTION ─────────────────────────────
elif page == NAV_PAGES[1]:
    st.markdown("<h2 style='color:white;margin:0 0 4px;'>📊 Prediction</h2>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#9CA3AF;margin-bottom:20px;'>Run a detailed traffic forecast.</p>",
                unsafe_allow_html=True)
    p1, p2 = st.columns([1.1, 0.9], gap="medium")
    with p1:
        _predict_card(suffix="_pred")
    with p2:
        with st.container(border=True):
            html('<p class="card-title">📊 Traffic Level</p>')
            _render_result_card()

# ─────────────────── ANALYTICS ──────────────────────────────
elif page == NAV_PAGES[2]:
    st.markdown("<h2 style='color:white;margin:0 0 4px;'>📈 Analytics</h2>",
                unsafe_allow_html=True)
    st.markdown("<p style='color:#9CA3AF;margin-bottom:20px;'>"
                "Traffic trend analysis across hours, days and weather.</p>",
                unsafe_allow_html=True)
    a1, a2 = st.columns(2, gap="medium")
    with a1:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;'>📉 Hourly Traffic</h3>",
                        unsafe_allow_html=True)
            tdata=[25,40,55,62,70,82,90,85,76,65,58,62,70,80,88,92,85,78,72,65,55,48,35,28]
            fig=px.area(pd.DataFrame({"Hour":list(range(24)),"Traffic":tdata}),
                        x="Hour",y="Traffic",color_discrete_sequence=["#6D5DFB"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                              font_color="white",height=280,margin=dict(l=0,r=0,t=10,b=0))
            fig.update_xaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            fig.update_yaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            st.plotly_chart(fig,use_container_width=True)
    with a2:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;'>📅 Day-of-Week Pattern</h3>",
                        unsafe_allow_html=True)
            fig2=px.bar(pd.DataFrame({"Day":["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
                                      "Traffic":[72,68,75,80,88,55,42]}),
                        x="Day",y="Traffic",color_discrete_sequence=["#6D5DFB"])
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                               font_color="white",height=280,margin=dict(l=0,r=0,t=10,b=0))
            fig2.update_xaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            fig2.update_yaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            st.plotly_chart(fig2,use_container_width=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)
    a3, a4 = st.columns(2, gap="medium")
    with a3:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;'>🌦️ Weather vs Congestion</h3>",
                        unsafe_allow_html=True)
            fig3=px.bar(pd.DataFrame({"Weather":["Clear","Clouds","Rain"],
                                      "Congestion":[42,65,88],"Color":["#22c55e","#facc15","#ff6b6b"]}),
                        x="Weather",y="Congestion",color="Color",
                        color_discrete_map={"#22c55e":"#22c55e","#facc15":"#facc15","#ff6b6b":"#ff6b6b"})
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                               font_color="white",height=260,margin=dict(l=0,r=0,t=10,b=0),
                               showlegend=False)
            fig3.update_xaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            fig3.update_yaxes(color="#9CA3AF",gridcolor="#243041",zeroline=False)
            st.plotly_chart(fig3,use_container_width=True)
    with a4:
        with st.container(border=True):
            st.markdown("<h3 style='color:white;font-size:14px;'>🥧 Traffic Distribution</h3>",
                        unsafe_allow_html=True)
            fig4=px.pie(pd.DataFrame({"Level":["Low","Medium","High"],"Count":[40,35,25]}),
                        values="Count",names="Level",hole=0.55,
                        color_discrete_sequence=["#22c55e","#facc15","#ff6b6b"])
            fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)",font_color="white",
                               height=260,margin=dict(l=0,r=0,t=10,b=0),
                               legend=dict(font=dict(color="white"),bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig4,use_container_width=True)

# ─────────────────── HISTORY ────────────────────────────────
elif page == NAV_PAGES[4]:
    st.markdown("<h2 style='color:white;margin:0 0 4px;'>🕑 Prediction History</h2>",
                unsafe_allow_html=True)
    with st.container(border=True):
        if st.session_state.history:
            st.dataframe(pd.DataFrame(st.session_state.history),
                         use_container_width=True, hide_index=True)
            if st.button("🗑️ Clear History"):
                st.session_state.history = []
                st.rerun()
        else:
            st.markdown("<p style='color:#9CA3AF;padding:20px 0;'>"
                        "No history yet. Go to Dashboard and run a prediction.</p>",
                        unsafe_allow_html=True)

# ─────────────────── OTHER PAGES ────────────────────────────
else:
    page_name = page.split("  ", 1)[-1]
    html(f"""
        <div class="coming-soon">
            🚧
            <p>{page_name}</p>
            <p style="font-size:13px;color:#6B7280;margin-top:4px;">
                This section is under development.
            </p>
        </div>
    """)

# ════════════════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════════════════
html("""
    <div style="text-align:center;color:#9CA3AF;font-size:12px;
                margin:28px 0 12px;padding-top:16px;border-top:1px solid #243041;">
        🚦 Smart Traffic Prediction System &nbsp;|&nbsp;
        AI + Machine Learning + Streamlit
    </div>
""")
