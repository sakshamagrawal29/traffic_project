import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from datetime import datetime
import random

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Traffic Prediction System",
    page_icon="🚦",
    layout="wide"
)

# ---------------- LOAD MODEL ----------------
model = joblib.load("traffic_model.pkl")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

[data-testid="collapsedControl"] {
    display: none;
}


.main {
    background-color: #050816;
    color: white;
}

.stApp {
    background-color: #050816;
}

h1,h2,h3,h4,h5,h6,p,label {
    color: white !important;
}

[data-testid="stSidebar"] {
    background-color: #0b1023;
}

.metric-box {
    background: linear-gradient(135deg,#111827,#1f2937);
    padding: 20px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0px 0px 15px rgba(128,0,255,0.3);
}

.big-font {
    font-size: 28px !important;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:

    st.image("https://cdn-icons-png.flaticon.com/512/3202/3202926.png", width=80)

    selected = option_menu(
        menu_title="Traffic System",
        options=[
            "Dashboard",
            "Analytics",
            "Traffic Map",
            "History",
            "About"
        ],
        icons=[
            "speedometer2",
            "bar-chart",
            "geo-alt",
            "clock-history",
            "info-circle"
        ],
        default_index=0,
        styles={
            "container": {
                "background-color": "#0b1023"
            },
            "icon": {
                "color": "white",
                "font-size": "18px"
            },
            "nav-link": {
                "color": "white",
                "font-size": "16px",
                "text-align": "left",
                "margin":"5px"
            },
            "nav-link-selected": {
                "background-color": "#7c3aed"
            },
        }
    )

# ---------------- HEADER ----------------

# ---------------- TOP METRICS ----------------
metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric("🚗 Total Vehicles", random.randint(1000,5000))

with metric2:
    st.metric("⚡ Avg Speed", f"{random.randint(30,80)} km/h")

with metric3:
    st.metric("🚨 Congestion", f"{random.randint(40,90)}%")

with metric4:
    st.metric("🤖 AI Status", "Online")

accuracy_col1, accuracy_col2 = st.columns(2)

with accuracy_col1:
    st.success("✅ Model Accuracy: 92%")

with accuracy_col2:
    st.info("🌐 System Status: Active")

st.divider()


col1, col2, col3 = st.columns([4,1,1])

with col1:
    st.title("🚦 Traffic Prediction Dashboard")
    st.write("AI Powered Smart City Traffic Management")

with col2:
    st.metric("Temperature", "28°C")

with col3:
    current_time = datetime.now().strftime("%I:%M %p")
    st.metric("Time", current_time)

st.divider()

# ---------------- INPUT SECTION ----------------
left, right = st.columns([1,1])

with left:

    st.subheader("Prediction Inputs")

    city = st.selectbox(
        "Select City",
        ["Jaipur", "Patna", "Samastipur"]
    )

    day = st.selectbox(
        "Select Day",
        [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]
    )

    weather = st.selectbox(
        "Weather",
        ["Clear", "Clouds", "Rain"]
    )

    road = st.selectbox(
        "Road Condition",
        ["Dry", "Wet"]
    )

with right:

    st.subheader("Traffic Parameters")

    hour = st.slider("Hour",0,23,10)

    vehicle_count = st.slider(
        "Vehicle Count",
        0,
        500,
        200
    )

    avg_speed = st.slider(
        "Average Speed",
        0,
        120,
        60
    )

# ---------------- ENCODING ----------------
city_map = {
    "Jaipur":0,
    "Patna":1,
    "Samastipur":2
}

weather_map = {
    "Clear":0,
    "Clouds":1,
    "Rain":2
}

road_map = {
    "Dry":0,
    "Wet":1
}

day_map = {
    "Monday":1,
    "Tuesday":5,
    "Wednesday":6,
    "Thursday":4,
    "Friday":0,
    "Saturday":2,
    "Sunday":3
}

# ---------------- PREDICTION ----------------
if st.button("🚀 Predict Traffic"):

    input_data = pd.DataFrame([[
        city_map[city],
        hour,
        day_map[day],
        weather_map[weather],
        road_map[road],
        vehicle_count,
        avg_speed
    ]],
    columns=[
        'city',
        'hour',
        'day',
        'weather_main',
        'road_condition',
        'vehicle_count',
        'avg_speed'
    ])

    prediction = model.predict(input_data)

    # ---------------- RESULT ----------------
    st.divider()

    result_col1, result_col2 = st.columns([1,1])

    if prediction[0] == 0:
        traffic_text = "Low Traffic"
        traffic_value = 25
        traffic_color = "green"

    elif prediction[0] == 1:
        traffic_text = "Medium Traffic"
        traffic_value = 60
        traffic_color = "orange"

    else:
        traffic_text = "High Traffic"
        traffic_value = 90
        traffic_color = "red"

    with result_col1:

        st.subheader("Prediction Result")

        gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = traffic_value,
            title = {'text': traffic_text},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': traffic_color},
                'steps': [
                    {'range': [0, 40], 'color': "green"},
                    {'range': [40, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "red"}
                ],
            }
        ))

        gauge.update_layout(
            paper_bgcolor="#050816",
            font={'color': "white"}
        )

        st.plotly_chart(gauge, use_container_width=True)

    with result_col2:

        st.subheader("Traffic Status")

        if prediction[0] == 0:
            st.success("✅ Low Congestion Expected")

        elif prediction[0] == 1:
            st.warning("⚠️ Medium Congestion Expected")

        else:
            st.error("🚨 High Congestion Expected")

        st.metric("Congestion Level", f"{traffic_value}%")
        st.metric("Vehicles", vehicle_count)
        st.metric("Average Speed", f"{avg_speed} km/h")

# ---------------- ANALYTICS SECTION ----------------
st.divider()

st.subheader("📊 Traffic Analytics")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    hours = list(range(24))
    traffic_data = [25,40,55,62,70,82,90,85,76,65,58,62,70,80,88,92,85,78,72,65,55,48,35,28]

    line_df = pd.DataFrame({
        "Hour":hours,
        "Traffic":traffic_data
    })

    fig1 = px.line(
        line_df,
        x="Hour",
        y="Traffic",
        title="Traffic By Hour"
    )

    fig1.update_layout(
        paper_bgcolor="#050816",
        plot_bgcolor="#050816",
        font_color="white"
    )

    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:

    area_df = pd.DataFrame({
        "Area":[
            "C-Scheme",
            "MI Road",
            "Vaishali Nagar",
            "Malviya Nagar"
        ],
        "Traffic":[78,65,50,35]
    })

    fig2 = px.bar(
        area_df,
        x="Area",
        y="Traffic",
        title="Top Congested Areas"
    )

    fig2.update_layout(
        paper_bgcolor="#050816",
        plot_bgcolor="#050816",
        font_color="white"
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------------- HEATMAP ----------------
st.divider()

st.subheader("🗺️ Traffic Heat Map")
st.caption("Live congestion monitoring across city routes")

map_data = pd.DataFrame({
    'lat':[26.9124,26.90,26.89,26.93],
    'lon':[75.7873,75.80,75.75,75.82]
})

st.map(map_data)

# ---------------- DYNAMIC PREDICTION HISTORY ----------------

if 'history' not in st.session_state:
    st.session_state.history = []

try:
    st.session_state.history.append({
        "City": city,
        "Traffic": traffic_text if 'traffic_text' in locals() else "No Prediction Yet",
        "Vehicles": vehicle_count,
        "Speed": avg_speed
    })
except:
    pass

# ---------------- RECENT PREDICTIONS ----------------
st.divider()

st.subheader("📝 Recent Predictions")

history_df = pd.DataFrame(st.session_state.history)

st.dataframe(history_df, use_container_width=True)

# ---------------- FOOTER ----------------
st.divider()
st.caption("🚦 Smart Traffic Prediction System | AI + Machine Learning + Streamlit Dashboard")