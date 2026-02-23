import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import os

from database import init_db, insert_incident, get_all_incidents
from auth import create_default_users, login
# Ensure get_safety_chatbot_response is imported from your ai_analysis file
from ai_analysis import analyze_incidents, get_safety_chatbot_response

# -----------------------------
# 1. Initialize System
# -----------------------------
init_db()
create_default_users()
UPLOAD_DIR = "uploaded_evidence"  # This defines the variable name
if not os.path.exists(UPLOAD_DIR): # This creates the actual folder on your PC
    os.makedirs(UPLOAD_DIR)

st.set_page_config(page_title="Water Metro Safety", layout="wide")

# -----------------------------
# 2. THEME, DE-BRANDING & FLOATING CHAT CSS
# -----------------------------
st.markdown(f"""
<style>
/* Hide Streamlit Branding & Creator Profile */
# header {{visibility: hidden;}}
# footer {{visibility: hidden;}}
# #MainMenu {{visibility: hidden;}}
# [data-testid="stSidebarNav"] + div {{display: none;}}
# [data-testid="stSidebarFooter"] {{display: none;}}
# .stDeployButton {{display:none;}}

/* Main App Background - Deep Midnight Blue */
.stApp {{
    background-color: #0e1b2a;
    color: white;
}}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    background-color: #07111d;
    border-right: 1px solid rgba(162, 255, 255, 0.1);
}}

/* Headers and Text */
h1, h2, h3, p, label, .stMarkdown {{
    color: white !important;
}}

/* Metrics Styling */
# div[data-testid="stMetricValue"] > div {{
#     color: #a2ffff !important;
#     font-weight: 800;
# }}

/* Input Fields */
# input, textarea, select {{
#     background-color: #ffffff !important;
#     color: #0e1b2a !important;
#     border-radius: 5px !important;
# }}

/* Incident Cards (Glassmorphism Effect) */
.incident-card {{
    background-color: rgba(255, 255, 255, 0.05);
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #a2ffff;
    margin-bottom: 20px;
}}

/* Horizontal Line */
hr {{
    border-color: rgba(162, 255, 255, 0.2) !important;
}}

/* FLOATING CHATBOT POSITIONING */
/* This targets the container for the popover */
div[data-testid="stPopover"] {{
    position: fixed;
    bottom: 70px;
    right: 30px;
    z-index: 1000;
    width: 65px;
}}

/* Styling the popover button to look like a teal chat bubble */
div[data-testid="stPopover"] > button {{
    border-radius: 50% !important;
    width: 65px !important;
    height: 65px !important;
    background-color: #a2ffff !important;
    color: #0e1b2a !important;
    border: none !important;
    box-shadow: 0px 4px 15px rgba(162, 255, 255, 0.4) !important;
    font-size: 24px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
}}

/* Adjust the popup window to open upwards from the button */
div[data-testid="stPopoverBody"] {{
    position: absolute !important;
    bottom: 80px !important;
    left: 0px !important;    /* Keeps it aligned to your left-side button */
    right: auto !important;

    /* DYNAMIC SIZING PROPERTIES */
    width: auto !important;      /* Allows width to shrink-to-fit content */
    min-width: 250px !important; /* Prevents it from being too skinny */
    max-width: 450px !important; /* Prevents it from covering the whole screen */
    
    height: auto !important; 
    min-height: 250px !important;    /* Allows height to grow with content */
    max-height: 500px !important;/* Adds a scrollbar if content is too long */
    
    overflow-y: auto !important; /* Enables scrolling for long content */
    display: flex !important;
    flex-direction: column !important;
}}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 3. HEADER SECTION
# -----------------------------
header_col1, header_col2 = st.columns([1, 6])

with header_col1:
    try:
        st.image("assets/logo.png", width=100)
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

    # =====================================
    # OFFICER PANEL
    # =====================================
    if st.session_state.role == "Officer":
        st.subheader("📝 New Incident Report")

        with st.form("incident_entry"):
            terminal = st.selectbox("Terminal Location", [
                "High Court", "Vyttila", "Kakkanad", "Fort Kochi", 
                "Vypin", "Bolgatty", "South Chittoor", "Cheranallur", 
                "Eloor", "Mulavukad North", "Willingdon Island", "Mattancherry"
            ])
            incident_type = st.selectbox("Incident Category", ["Mechanical", "Electrical", "Injury", "Security", "Environmental"])
            severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
            description = st.text_area("Observations / Details")
            action_taken = st.text_area("Immediate Response Taken")

            st.write("📸 **Evidence Upload**")
            up_file = st.file_uploader("Upload Image/PDF", type=['png', 'jpg', 'jpeg', 'pdf'])

            if st.form_submit_button("Submit Report"):
                file_path = None
                if up_file:
                    file_path = os.path.join(UPLOAD_DIR, up_file.name)
                    with open(file_path, "wb") as f:
                        f.write(up_file.getbuffer())
                insert_incident((terminal, incident_type, severity, description, action_taken, str(datetime.datetime.now()),file_path))
                st.success("✅ Report Synced to Command Center.")

    # =====================================
    # ADMIN PANEL
    # =====================================
    elif st.session_state.role == "Admin":
        st.subheader("📊 Intelligent FRACAS")
        incidents = get_all_incidents()

        if incidents:
            df = pd.DataFrame(incidents, columns=["ID", "Terminal", "Incident Type", "Severity", "Description", "Action Taken", "Date","Evidence"])

            # --- 1. KPI METRICS ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Logs", len(df))
            m2.metric("Critical Alerts", len(df[df["Severity"] == "Critical"]))
            score = 100 - (len(df[df['Severity'] == 'Critical']) * 10)
            m3.metric("Safety Score", f"{max(score, 0)}%")
            
            csv = df.to_csv(index=False).encode('utf-8')
            m4.download_button("📥 Export CSV", data=csv, file_name=f'KMRL_Audit_{datetime.date.today()}.csv', mime='text/csv')

            st.markdown("---")
            
            # --- 2. INTERACTIVE ANALYTICS ---
            st.write("### 📈 Visual Risk Analytics")
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                t_data = df["Terminal"].value_counts().reset_index()
                t_data.columns = ["Terminal", "Count"]
                fig_t = px.bar(t_data, x="Terminal", y="Count", title="Incidents by Terminal", color_discrete_sequence=['#a2ffff'], template="plotly_dark")
                fig_t.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_t, use_container_width=True)
            
            with g_col2:
                s_data = df["Severity"].value_counts().reset_index()
                s_data.columns = ["Severity", "Count"]
                c_map = {"Critical": "#ff4d4d", "High": "#ffa31a", "Medium": "#33ccff", "Low": "#70db70"}
                fig_s = px.pie(s_data, values="Count", names="Severity", title="Risk Distribution", hole=0.5, color="Severity", color_discrete_map=c_map, template="plotly_dark")
                fig_s.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_s, use_container_width=True)

            st.markdown("---")

            # --- 3. FILTERED FEED ---
            terminal_filter = st.selectbox("Filter Feed by Location", ["Show All Terminals"] + list(df["Terminal"].unique()))
            display_df = df if terminal_filter == "Show All Terminals" else df[df["Terminal"] == terminal_filter]

            for _, row in display_df.iterrows():
                sev_color = {"Critical": "#ff4d4d", "High": "#ffa31a", "Medium": "#33ccff", "Low": "#70db70"}.get(row["Severity"], "white")
                card_html = f"""
<div class="incident-card">
<h3 style="margin:0; color: #a2ffff !important;">🏢 {row['Terminal']}</h3>
<p style="margin:5px 0; font-size: 0.9em;">
<b>TYPE:</b> {row['Incident Type']} | <b>SEVERITY:</b> <span style="color:{sev_color}; font-weight:bold;">{row['Severity'].upper()}</span> | <b>DATE:</b> {row['Date'][:10]}
</p>
<p style="opacity: 0.9; margin-top:10px;">{row['Description']}</p>
<div style="margin-top:10px; padding-top:10px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 0.85em;">
<b>RESPONSE:</b> {row['Action Taken']}
</div>
</div>"""
                st.markdown(card_html, unsafe_allow_html=True)
                # VIEW UPLOADED EVIDENCE

                # if row['Evidence'] and os.path.exists(row['Evidence']):
                #     with st.expander("👁️ View Evidence"):
                #         if row['Evidence'].lower().endswith(('.png', '.jpg', '.jpeg')):
                #             st.image(row['Evidence'], use_container_width=True)
                #         else:
                #             with open(row['Evidence'], "rb") as f:
                #                 st.download_button("📥 Download PDF", f, file_name=os.path.basename(row['Evidence']), key=f"feed_dl_{row['ID']}")
                # st.write("")
                # --- 4. Global Evidence Vault (OUTSIDE THE LOOP) ---
            st.markdown("---")
            st.write("### 📁 Evidence Explorer (All Files)")
            all_files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))]
            
            if all_files:
                selected_filename = st.selectbox("Select file to download:", all_files, key="global_vault_selector")
                if selected_filename:
                    f_path = os.path.join(UPLOAD_DIR, selected_filename)
                    with open(f_path, "rb") as f:
                        st.download_button(f"Download {selected_filename}", f, file_name=selected_filename, key="vault_dl_btn")
            else:
                st.info("No files uploaded yet.")

            # --- 4. FLOATING CHATBOT ICON ---
            # The div wrapper is no longer strictly needed because CSS targets stPopover directly
            with st.popover("💬"):
                st.markdown("### 💬 Safety Advisor")
                st.caption("General Work Site Safety & Security Assistant")
                
                if "messages" not in st.session_state:
                    st.session_state.messages = []

                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                if prompt := st.chat_input("Ask a safety question..."):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.markdown(prompt)

                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = get_safety_chatbot_response(prompt)
                            st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

            # AI Audit Button
            st.markdown("---")
            if st.button("🤖 Run Advanced AI Fleet Audit"):
                with st.spinner("Processing safety data..."):
                    result = analyze_incidents(incidents)
                st.info(result)

        else:
            st.info("No safety logs found in the database.")