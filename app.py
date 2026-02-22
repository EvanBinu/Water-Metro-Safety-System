import streamlit as st
import pandas as pd
import datetime

from database import init_db, insert_incident, get_all_incidents
from auth import create_default_users, login
from ai_analysis import analyze_incidents

# -----------------------------
# 1. Initialize System
# -----------------------------
init_db()
create_default_users()

st.set_page_config(page_title="Water Metro Safety", layout="wide")

# -----------------------------
# 2. THEME & COLOR CUSTOMIZATION
# -----------------------------
st.markdown("""
    <style>
    /* 1. Hide the Streamlit Header and Footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 2. Hide the Main Menu (Hamburger menu) */
    #MainMenu {visibility: hidden;}
    
    /* 3. Hide the Sidebar "Created by" profile and Streamlit logo */
    [data-testid="stSidebarNav"] + div {display: none;}
    [data-testid="stSidebarFooter"] {display: none;}
    
    /* 4. Hide the "Deploy" button and other cloud-specific decorations */
    .stDeployButton {display:none;}
    .st-emotion-cache-1647it7 {display: none;} /* This targets the specific viewer badge */

    /* Optional: Remove top padding so the app starts at the very top */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown(f"""
<style>
.stApp {{
    background-color: #0e1b2a;
    color: white;
}}

[data-testid="stSidebar"] {{
    background-color: #07111d;
    border-right: 1px solid rgba(162, 255, 255, 0.1);
}}

h1, h2, h3, p, label, .stMarkdown {{
    color: white !important;
}}

/* Metrics Styling */
div[data-testid="stMetricValue"] > div {{
    color: #a2ffff !important;
    font-weight: 800;
}}

input, textarea, select {{
    background-color: #ffffff !important;
    color: #0e1b2a !important;
    border-radius: 5px !important;
}}

.incident-card {{
    background-color: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #a2ffff;
    margin-bottom: 20px;
}}

hr {{
    border-color: rgba(162, 255, 255, 0.2) !important;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 3. HEADER SECTION
# -----------------------------
header_col1, header_col2 = st.columns([1, 6])

with header_col1:
    try:
        st.image("assets/logo.png", width=200)
    except Exception:
        st.error("Logo missing")

with header_col2:
    st.markdown("""
<div style="padding-top: 5px;">
<h1 style="margin-bottom: 0px; color: #a2ffff !important;">Water Metro Safety System</h1>
<p style="opacity: 0.8; font-size: 1.1em; letter-spacing: 1px;">KOCHI METRO RAIL LIMITED | AUDIT PORTAL</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# 4. SESSION STATE & AUTH
# -----------------------------
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.role is None:
    _, login_box, _ = st.columns([1, 1.5, 1])
    with login_box:
        st.subheader("🔐 Authentication")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Authenticate"):
            role = login(username, password)
            if role:
                st.session_state.role = role
                st.success("Access Granted")
                st.rerun()
            else:
                st.error("Invalid Credentials")

# -----------------------------
# 5. DASHBOARD PANELS
# -----------------------------
else:
    st.sidebar.markdown(f"### Welcome, \n**{st.session_state.role}**")
    if st.sidebar.button("Logout", type="secondary"):
        st.session_state.role = None
        st.rerun()

    if st.session_state.role == "Officer":
        st.subheader("📝 New Incident Report")
        with st.form("incident_entry"):
            terminal = st.selectbox("Terminal Location", ["High Court", "Vyttila", "Kakkanad", "Fort Kochi", "Vypin", "Bolgatty", "South Chittoor", "Cheranallur", "Eloor", "Mulavukad North", "Willingdon Island", "Mattancherry"])
            incident_type = st.selectbox("Incident Category", ["Mechanical", "Electrical", "Injury", "Security", "Environmental"])
            severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
            description = st.text_area("Observations / Details")
            action_taken = st.text_area("Immediate Response Taken")

            if st.form_submit_button("Submit Report"):
                insert_incident((terminal, incident_type, severity, description, action_taken, str(datetime.datetime.now())))
                st.success("✅ Report Synced.")

    elif st.session_state.role == "Admin":
        st.subheader("📊 Fleet Safety Intelligence")
        incidents = get_all_incidents()

        if incidents:
            df = pd.DataFrame(incidents, columns=["ID", "Terminal", "Incident Type", "Severity", "Description", "Action Taken", "Date"])
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Logs", len(df))
            kpi2.metric("Critical Alerts", len(df[df["Severity"] == "Critical"]))
            kpi3.metric("Fleet Status", "Stable")

            st.markdown("---")
            terminal_filter = st.selectbox("Filter Feed", ["Show All Terminals"] + list(df["Terminal"].unique()))
            if terminal_filter != "Show All Terminals":
                df = df[df["Terminal"] == terminal_filter]

            for _, row in df.iterrows():
                sev_color = {"Critical": "#ff4d4d", "High": "#ffa31a", "Medium": "#33ccff", "Low": "#70db70"}.get(row["Severity"], "white")
                
                # HTML block with zero indentation
                card_html = f"""
<div class="incident-card">
<h3 style="margin:0; color: #a2ffff !important;">🏢 {row['Terminal']}</h3>
<p style="margin:5px 0; font-size: 0.9em;">
<b>TYPE:</b> {row['Incident Type']} | 
<b>SEVERITY:</b> <span style="color:{sev_color}; font-weight:bold;">{row['Severity'].upper()}</span> | 
<b>DATE:</b> {row['Date'][:10]}
</p>
<p style="opacity: 0.9; margin-top:10px;">{row['Description']}</p>
<div style="margin-top:10px; padding-top:10px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 0.85em;">
<b>RESPONSE:</b> {row['Action Taken']}
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)

            st.markdown("---")
            if st.button("🤖 Run AI Fleet Audit"):
                with st.spinner("Analyzing..."):
                    result = analyze_incidents(incidents)
                st.info(result)