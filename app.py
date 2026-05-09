import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random
import textwrap

# ── Helper: strips Python indentation before passing HTML to st.markdown.
# Without this, lines indented 4+ spaces are treated as Markdown code blocks,
# causing raw HTML to appear as source code instead of rendered output.
def render_html(html_str: str):
    """Dedent + render an HTML string safely."""
    st.markdown(textwrap.dedent(html_str).strip(), unsafe_allow_html=True)

# ════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════
st.set_page_config(
    page_title="Traffic Prediction System",
    page_icon="🚦",
    layout="wide"
)

# ════════════════════════════════════════════════
#  LOAD MODEL
# ════════════════════════════════════════════════
model = joblib.load("traffic_model.pkl")

# ════════════════════════════════════════════════
#  INJECT FONTS + ICONS + FULL CSS
# ════════════════════════════════════════════════
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.css" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>

<style>

/* ───────────── HIDE STREAMLIT CHROME ───────────── */
#MainMenu, header[data-testid="stHeader"], footer          { display: none !important; }
[data-testid="collapsedControl"]                           { display: none !important; }
.block-container                                           { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebarContent"]                    { padding: 0 !important; }

/* ───────────── GLOBAL ───────────── */
*, *::before, *::after { font-family: 'Poppins', sans-serif !important; box-sizing: border-box; }
body                   { background-color: #070F1F !important; margin: 0; padding: 0; }
.stApp, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0b132b 0%, #1c2541 50%, #3a506b 100%) !important;
}

/* ───────────── NAVBAR ───────────── */
#navbar {
    height: 75px;
    display: flex;
    align-items: center;
    padding: 0 25px;
    background-color: #0f1937;
    color: white;
    position: sticky;
    top: 0;
    z-index: 999;
    width: 100%;
}
#logo                { display: flex; align-items: center; gap: 12px; }
#logo-text           { display: flex; flex-direction: column; }
#logo h1             { font-size: 20px; margin: 0; color: white !important; font-weight: 600; }
#logo p              { font-size: 11px; color: #9CA3AF; margin: 0; }
#logo i              { font-size: 28px; color: #8274ff; }
#nav-right           { display: flex; align-items: center; gap: 20px; margin-left: auto; }
#first, #second, #third {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border: 1px solid #243041;
    border-radius: 100px;
    box-shadow: 0 0 0 1px rgba(59,130,246,0.08), 0 4px 20px rgba(0,0,0,0.35);
    transition: all 0.3s ease;
    color: white;
    padding: 8px 16px;
}
#first:hover, #second:hover, #third:hover {
    border-color: rgba(59,130,246,0.4);
    box-shadow: 0 0 5px rgba(59,130,246,0.25), 0 0 5px rgba(95,196,28,0.15);
    transform: translateY(-3px);
}
#first h4, #second h4, #third h4 { font-size: 13px; font-weight: 500; color: white; margin: 0; }

/* ───────────── STREAMLIT SIDEBAR ───────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(to bottom, #141E30, #243B55) !important;
    border-right: 1px solid #243041 !important;
    min-width: 250px !important;
    max-width: 250px !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 15px !important; }

/* ───────────── SIDEBAR NAV ITEMS ───────────── */
.nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 15px;
    color: white;
    transition: all 0.3s ease;
    cursor: pointer;
    font-size: 15px;
    font-weight: 500;
    margin: 2px 0;
    text-decoration: none;
}
.nav-item:hover { background-color: rgba(255,255,255,0.08); transform: translateX(4px); }
.nav-item i    { color: #6D5DFB; font-size: 18px; }
.active-nav    { background-color: #6D5DFB !important; }
.active-nav i  { color: white !important; }
#side-card {
    margin-top: 20px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    border: 1px solid #243041;
    border-radius: 18px;
    box-shadow: 0 0 0 1px rgba(59,130,246,0.08), 0 4px 20px rgba(0,0,0,0.35);
    padding: 15px;
    text-align: center;
    transition: all 0.3s ease;
}
#side-card:hover {
    border-color: rgba(64,0,254,0.4);
    box-shadow: 0 0 5px rgba(59,130,246,0.25), 0 0 5px rgba(95,196,28,0.15);
    transform: translateY(-3px);
}
#side-card h4 { color: white !important; margin: 8px 0 4px; font-size: 14px; }
#side-card p  { color: #9CA3AF !important; font-size: 12px; margin: 0; }

/* ───────────── CARD CONTAINERS ───────────── */
/* Target Streamlit bordered containers */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.05) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid #243041 !important;
    border-radius: 15px !important;
    box-shadow: 0 0 0 1px rgba(59,130,246,0.08), 0 4px 20px rgba(0,0,0,0.35) !important;
    transition: all 0.3s ease !important;
    padding: 10px !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    border-color: rgba(59,130,246,0.4) !important;
    box-shadow: 0 0 15px rgba(59,130,246,0.25), 0 0 50px rgba(95,196,28,0.15) !important;
    transform: translateY(-4px) !important;
}

/* Card heading styles */
.card-title {
    font-size: 20px;
    font-weight: 600;
    color: white !important;
    margin: 0 0 4px 0;
}
.card-subtitle { font-size: 12px; color: #9CA3AF; margin: 0 0 18px 0; }

/* ───────────── INPUT WIDGETS ───────────── */
.stSelectbox label, .stSlider label, .stNumberInput label {
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
/* Slider track + thumb */
[data-baseweb="slider"] [data-testid="stTickBar"] { color: #9CA3AF !important; }
.stSlider [role="slider"]         { background-color: #6D5DFB !important; }
[data-baseweb="slider"] div[data-baseweb="slider-track-fill"] { background: #6D5DFB !important; }

/* ───────────── PREDICT BUTTON ───────────── */
.stButton > button {
    background: linear-gradient(135deg, #6D5DFB, #4f46e5) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 24px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    width: 100% !important;
    margin-top: 12px !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 25px rgba(109,93,251,0.55) !important;
}
.stButton > button:active { transform: translateY(0px) !important; }

/* ───────────── RESULT (LEVEL) CARD ───────────── */
.result-content {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 15px;
    gap: 10px;
}
.traffic-wrapper {
    position: relative;
    width: 105px;
    height: 105px;
    flex-shrink: 0;
}
.ring {
    width: 105px;
    height: 105px;
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
.traffic-wrapper i {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 24px;
    color: white;
    z-index: 5;
    animation: floatCar 2s ease-in-out infinite;
}
.left-result { display: flex; flex-direction: column; align-items: center; }
.traffic-level {
    font-size: 32px;
    margin-top: 12px;
    letter-spacing: 2px;
    font-weight: 700;
    text-shadow: 0 0 20px rgba(255,77,77,0.25);
}
.traffic-level.awaiting {
    background: linear-gradient(90deg, #9CA3AF, #6B7280);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.traffic-level.low {
    background: linear-gradient(90deg, #22c55e, #16a34a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.traffic-level.medium {
    background: linear-gradient(90deg, #facc15, #f59e0b, #ff7b00);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.traffic-level.high {
    background: linear-gradient(90deg, #ffb800, #ff7b00, #ff3b3b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.traffic-status { color: #AEB6C8; margin-top: -5px; font-size: 14px; }

.traffic-info { display: flex; flex-direction: column; gap: 10px; }
.info-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 10px 14px;
    min-width: 120px;
    backdrop-filter: blur(10px);
    transition: all 0.45s cubic-bezier(0.22,1,0.36,1);
}
.info-box:hover {
    border-color: rgba(64,0,254,0.4);
    box-shadow: 0 0 5px rgba(59,130,246,0.25), 0 0 5px rgba(95,196,28,0.15);
    transform: translateY(-5px);
}
.info-box h4     { font-size: 11px; color: #9CA3AF; margin: 0 0 4px 0; }
.info-box span   { color: white; font-size: 17px; font-weight: 600; }

/* Congestion badges */
.badge-high {
    color: #ff6b6b !important; font-size: 0.85rem !important; font-weight: 700 !important;
    letter-spacing: 1px !important;
    background: linear-gradient(135deg, rgba(113,34,34,0.55), rgba(193,43,43,0.78), rgba(179,57,57,0.25));
    border-radius: 10px; border: 1px solid rgba(255,144,144,0.18);
    padding: 4px 10px; text-shadow: 0 0 12px rgba(255,77,77,0.35);
}
.badge-medium {
    color: #facc15 !important; font-size: 0.85rem !important; font-weight: 700 !important;
    letter-spacing: 1px !important;
    background: rgba(234,179,8,0.2);
    border-radius: 10px; border: 1px solid rgba(234,179,8,0.3);
    padding: 4px 10px;
}
.badge-low {
    color: #22c55e !important; font-size: 0.85rem !important; font-weight: 700 !important;
    letter-spacing: 1px !important;
    background: rgba(34,197,94,0.2);
    border-radius: 10px; border: 1px solid rgba(34,197,94,0.3);
    padding: 4px 10px;
}

/* ───────────── PLOTLY ───────────── */
.js-plotly-plot, .plot-container { background: transparent !important; }

/* ───────────── STREAMLIT METRICS ───────────── */
[data-testid="stMetricValue"]             { color: white !important; font-size: 22px !important; }
[data-testid="stMetricLabel"]             { color: #9CA3AF !important; }
[data-testid="stMetricDeltaIcon-Up"]      { color: #22c55e !important; }
[data-testid="stMetricDeltaIcon-Down"]    { color: #ff6b6b !important; }

/* ───────────── DATAFRAME ───────────── */
[data-testid="stDataFrameResizable"]       { border-radius: 12px !important; overflow: hidden; }
.dvn-scroller                              { background: rgba(255,255,255,0.03) !important; }
.stDataFrame th                            { background: #1c2541 !important; color: white !important; }
.stDataFrame td                            { color: #d1d5db !important; }

/* ───────────── DIVIDER ───────────── */
[data-testid="stDivider"] hr { border-color: #243041 !important; }

/* ───────────── ANIMATIONS ───────────── */
@keyframes rotateRing {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes floatCar {
    0%   { transform: translate(-50%, -50%); }
    50%  { transform: translate(-50%, -58%); }
    100% { transform: translate(-50%, -50%); }
}

/* ───────────── SPACING HELPERS ───────────── */
.spacer-sm { margin-top: 12px; }
.spacer-md { margin-top: 20px; }
[data-testid="column"] { padding: 0 6px !important; }

</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════
#  NAVBAR
# ════════════════════════════════════════════════
current_time = datetime.now().strftime("%I:%M %p")
current_date = datetime.now().strftime("%d %b %Y")

render_html(f"""
    <div id="navbar">
        <div id="logo">
            <i class="ri-car-fill"></i>
            <div id="logo-text">
                <h1>Traffic Prediction System</h1>
                <p>Smart City, Better City</p>
            </div>
        </div>
        <div id="nav-right">
            <div id="first"><h4>🌤️ 28°C</h4></div>
            <div id="second"><h4>📅 {current_date}</h4></div>
            <div id="third"><h4>🕒 {current_time}</h4></div>
        </div>
    </div>
""")

# ════════════════════════════════════════════════
#  SIDEBAR — matches frontend slidebar exactly
# ════════════════════════════════════════════════
with st.sidebar:
    render_html("""
        <div class="nav-item active-nav">
            <i class="ri-dashboard-fill"></i> Dashboard
        </div>
        <div class="nav-item"><i class="ri-bar-chart-box-fill"></i> Prediction</div>
        <div class="nav-item"><i class="ri-line-chart-fill"></i> Analytics</div>
        <div class="nav-item"><i class="ri-map-pin-line"></i> Traffic Map</div>
        <div class="nav-item"><i class="ri-history-line"></i> History</div>
        <div class="nav-item"><i class="ri-notification-3-line"></i> Alerts</div>
        <div class="nav-item"><i class="ri-file-chart-line"></i> Reports</div>
        <div class="nav-item"><i class="ri-settings-3-line"></i> Settings</div>
        <div class="nav-item"><i class="ri-information-line"></i> About</div>
        <div id="side-card">
            <h4>Smart Traffic AI</h4>
            <p>Predict city traffic with AI analytics.</p>
        </div>
    """)

# ════════════════════════════════════════════════
#  SESSION STATE — stores prediction result across reruns
# ════════════════════════════════════════════════
if "traffic_text" not in st.session_state:
    st.session_state.traffic_text      = "——"
    st.session_state.traffic_class     = "awaiting"
    st.session_state.traffic_value     = 0
    st.session_state.traffic_color     = "#6B7280"
    st.session_state.congestion_badge  = '<span style="color:#9CA3AF;font-size:15px;font-weight:500;">Awaiting</span>'
    st.session_state.probability       = "—"
    st.session_state.status_text       = "Run a Prediction"

if "history" not in st.session_state:
    st.session_state.history = []

# ════════════════════════════════════════════════
#  TOP CARDS ROW — predict card  |  level card
# ════════════════════════════════════════════════
top_col1, top_col2 = st.columns([1.1, 0.9], gap="medium")

# ──────── LEFT: PREDICT CARD (with all input fields) ────────
with top_col1:
    with st.container(border=True):

        render_html('<p class="card-title">🔮 Predict Traffic</p>')
        render_html('<p class="card-subtitle">Fill the details below to get a traffic prediction</p>')

        # ── Two sub-columns matching the original left/right split ──
        left_in, right_in = st.columns(2, gap="small")

        with left_in:
            city = st.selectbox(
                "Select City",
                ["Jaipur", "Patna", "Samastipur"]
            )
            day = st.selectbox(
                "Select Day",
                ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
            )
            weather = st.selectbox(
                "Weather",
                ["Clear", "Clouds", "Rain"]
            )
            road = st.selectbox(
                "Road Condition",
                ["Dry", "Wet"]
            )

        with right_in:
            hour = st.slider("Hour", 0, 23, 10)
            vehicle_count = st.slider("Vehicle Count", 0, 500, 200)
            avg_speed = st.slider("Average Speed (km/h)", 0, 120, 60)

        predict_btn = st.button("🚀 Predict Traffic")

        # ── ENCODING (unchanged from original) ──
        city_map = {
            "Jaipur": 0,
            "Patna": 1,
            "Samastipur": 2
        }
        weather_map = {
            "Clear": 0,
            "Clouds": 1,
            "Rain": 2
        }
        road_map = {
            "Dry": 0,
            "Wet": 1
        }
        day_map = {
            "Monday": 1,
            "Tuesday": 5,
            "Wednesday": 6,
            "Thursday": 4,
            "Friday": 0,
            "Saturday": 2,
            "Sunday": 3
        }

        # ── PREDICTION LOGIC (unchanged from original) ──
        if predict_btn:

            input_data = pd.DataFrame([[
                city_map[city],
                hour,
                day_map[day],
                weather_map[weather],
                road_map[road],
                vehicle_count,
                avg_speed
            ]], columns=[
                'city', 'hour', 'day', 'weather_main',
                'road_condition', 'vehicle_count', 'avg_speed'
            ])

            prediction = model.predict(input_data)

            # ── RESULT MAPPING (unchanged logic) ──
            if prediction[0] == 0:
                traffic_text   = "LOW"
                traffic_value  = 25
                traffic_color  = "green"
                traffic_class  = "low"
                congestion_badge = '<span class="badge-low">LOW</span>'
                probability    = "25%"
                status_text    = "Light Traffic"

            elif prediction[0] == 1:
                traffic_text   = "MEDIUM"
                traffic_value  = 60
                traffic_color  = "orange"
                traffic_class  = "medium"
                congestion_badge = '<span class="badge-medium">MEDIUM</span>'
                probability    = "60%"
                status_text    = "Moderate Traffic"

            else:
                traffic_text   = "HIGH"
                traffic_value  = 90
                traffic_color  = "red"
                traffic_class  = "high"
                congestion_badge = '<span class="badge-high">HIGH</span>'
                probability    = "90%"
                status_text    = "Heavy Traffic"

            # Persist result to session state (survives rerun)
            st.session_state.traffic_text     = traffic_text
            st.session_state.traffic_class    = traffic_class
            st.session_state.traffic_value    = traffic_value
            st.session_state.traffic_color    = traffic_color
            st.session_state.congestion_badge = congestion_badge
            st.session_state.probability      = probability
            st.session_state.status_text      = status_text

            # Append to history (unchanged logic)
            st.session_state.history.append({
                "City":     city,
                "Traffic":  traffic_text,
                "Vehicles": vehicle_count,
                "Speed":    f"{avg_speed} km/h"
            })

# ──────── RIGHT: LEVEL CARD (result display) ────────
with top_col2:
    with st.container(border=True):

        render_html('<p class="card-title">📊 Traffic Level</p>')

        # ── Build the result HTML as a plain string first (no indentation in the
        #    string itself) so Markdown never mistakes the content for a code block.
        _tc   = st.session_state.traffic_class
        _tt   = st.session_state.traffic_text
        _ts   = st.session_state.status_text
        _cb   = st.session_state.congestion_badge
        _prob = st.session_state.probability

        result_html = (
            '<div class="result-content">'
                '<div class="left-result">'
                    '<div class="traffic-wrapper">'
                        '<div class="ring"></div>'
                        '<i class="ri-car-fill"></i>'
                    '</div>'
                    f'<h1 class="traffic-level {_tc}">{_tt}</h1>'
                    f'<p class="traffic-status">{_ts}</p>'
                '</div>'
                '<div class="traffic-info">'
                    '<div class="info-box">'
                        '<h4>Congestion</h4>'
                        f'{_cb}'
                    '</div>'
                    '<div class="info-box">'
                        '<h4>Probability</h4>'
                        f'<span>{_prob}</span>'
                    '</div>'
                    '<div class="info-box">'
                        '<h4>Status</h4>'
                        f'<span>{_ts}</span>'
                    '</div>'
                '</div>'
            '</div>'
        )
        st.markdown(result_html, unsafe_allow_html=True)

        # After prediction: also show a Plotly gauge (from original app.py logic)
        if st.session_state.traffic_value > 0:
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=st.session_state.traffic_value,
                title={"text": st.session_state.status_text, "font": {"color": "white"}},
                gauge={
                    "axis": {"range": [None, 100], "tickcolor": "white"},
                    "bar":  {"color": st.session_state.traffic_color},
                    "steps": [
                        {"range": [0, 40],  "color": "rgba(34,197,94,0.15)"},
                        {"range": [40, 70], "color": "rgba(250,204,21,0.15)"},
                        {"range": [70, 100],"color": "rgba(255,59,59,0.15)"}
                    ],
                    "bgcolor": "rgba(0,0,0,0)",
                    "bordercolor": "#243041"
                }
            ))
            gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "white"},
                height=200,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(gauge, use_container_width=True)

# ════════════════════════════════════════════════
#  BOTTOM CARDS ROW — three analytics cards
# ════════════════════════════════════════════════
st.markdown("<div class='spacer-md'></div>", unsafe_allow_html=True)

bot_col1, bot_col2, bot_col3 = st.columns(3, gap="medium")

# ──────── Traffic By Time of Day ────────
with bot_col1:
    with st.container(border=True):
        st.markdown("<h3 style='color:white;text-align:center;font-size:14px;margin-bottom:8px;'>Traffic By Time of Day</h3>", unsafe_allow_html=True)
        hours = list(range(24))
        traffic_data = [25,40,55,62,70,82,90,85,76,65,58,62,70,80,88,92,85,78,72,65,55,48,35,28]
        line_df = pd.DataFrame({"Hour": hours, "Traffic": traffic_data})
        fig1 = px.line(
            line_df, x="Hour", y="Traffic",
            color_discrete_sequence=["#6D5DFB"]
        )
        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", margin=dict(l=0, r=0, t=5, b=0), height=210
        )
        fig1.update_xaxes(color="#9CA3AF", gridcolor="#243041", zeroline=False)
        fig1.update_yaxes(color="#9CA3AF", gridcolor="#243041", zeroline=False)
        st.plotly_chart(fig1, use_container_width=True)

# ──────── Traffic By Day Type (Pie — matches frontend pie-chart) ────────
with bot_col2:
    with st.container(border=True):
        st.markdown("<h3 style='color:white;text-align:center;font-size:14px;margin-bottom:8px;'>Traffic By Day Type</h3>", unsafe_allow_html=True)
        pie_df = pd.DataFrame({
            "Type":    ["Weekday", "Weekend", "Holiday"],
            "Traffic": [75, 45, 30]
        })
        fig2 = px.pie(
            pie_df, values="Traffic", names="Type", hole=0.5,
            color_discrete_sequence=["#7a1f1f", "#2e8b57", "#3b82f6"]
        )
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font_color="white",
            margin=dict(l=0, r=0, t=5, b=0), height=210,
            legend=dict(font=dict(color="white"), bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig2, use_container_width=True)

# ──────── Weather Impact On Traffic ────────
with bot_col3:
    with st.container(border=True):
        st.markdown("<h3 style='color:white;text-align:center;font-size:14px;margin-bottom:8px;'>Weather Impact On Traffic</h3>", unsafe_allow_html=True)
        area_df = pd.DataFrame({
            "Area":    ["C-Scheme", "MI Road", "Vaishali Nagar", "Malviya Nagar"],
            "Traffic": [78, 65, 50, 35]
        })
        fig3 = px.bar(
            area_df, x="Area", y="Traffic",
            color_discrete_sequence=["#6D5DFB"]
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", margin=dict(l=0, r=0, t=5, b=0), height=210
        )
        fig3.update_xaxes(color="#9CA3AF", gridcolor="#243041", zeroline=False)
        fig3.update_yaxes(color="#9CA3AF", gridcolor="#243041", zeroline=False)
        st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════
#  RECENT PREDICTIONS (history table)
# ════════════════════════════════════════════════
st.markdown("<div class='spacer-md'></div>", unsafe_allow_html=True)
with st.container(border=True):
    st.markdown("<h3 style='color:white;font-size:16px;margin-bottom:10px;'>📝 Recent Predictions</h3>", unsafe_allow_html=True)
    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    else:
        st.markdown("<p style='color:#9CA3AF;font-size:13px;'>No predictions yet — run a prediction to see history here.</p>", unsafe_allow_html=True)

# ════════════════════════════════════════════════
#  FOOTER
# ════════════════════════════════════════════════
render_html("""
    <div style="text-align:center;color:#9CA3AF;font-size:12px;margin:24px 0 12px;padding-top:16px;border-top:1px solid #243041;">
        🚦 Smart Traffic Prediction System &nbsp;|&nbsp; AI + Machine Learning + Streamlit Dashboard
    </div>
""")
