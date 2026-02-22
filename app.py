import streamlit as st
import pandas as pd
import datetime

from database import init_db, insert_incident, get_all_incidents
from auth import create_default_users, login
from ai_analysis import analyze_incidents


# -----------------------------
# Initialize system
# -----------------------------
init_db()
create_default_users()

st.set_page_config(page_title="Water Metro Safety", layout="wide")
# Change this line in your code:
col1, col2 = st.columns([1, 5])

with col1:
    try:
        # Change this line in your code:
        st.image("assets/KMRL-logo.png", caption="KOCHI METRO RAIL LIMITED", width=150)
    except Exception:
        st.error("Logo not found")

with col2:
    # Markdown for better vertical alignment and subtitle
    st.markdown("""
        <div style="padding-top: 10px;">
            <h1 style="margin-bottom: 0px;">Water Metro Safety System</h1>

        </div>
    """, unsafe_allow_html=True)

st.markdown("---")
# -----------------------------
# Session State
# -----------------------------
if "role" not in st.session_state:
    st.session_state.role = None


# -----------------------------
# LOGIN SECTION
# -----------------------------
if st.session_state.role is None:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = login(username, password)
        if role:
            st.session_state.role = role
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


# -----------------------------
# AFTER LOGIN
# -----------------------------
else:

    st.sidebar.write(f"Logged in as: {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.role = None
        st.rerun()

    # =====================================
    # OFFICER PANEL
    # =====================================
    if st.session_state.role == "Officer":

        st.subheader("📝 Report Incident")

        terminal = st.selectbox(
            "Terminal",
            [
                "High Court", 
                "Vyttila", 
                "Kakkanad", 
                "Fort Kochi", 
                "Vypin", 
                "Bolgatty", 
                "South Chittoor", 
                "Cheranallur", 
                "Eloor", 
                "Mulavukad North", 
                "Willingdon Island", 
                "Mattancherry"
            ]
        )

        incident_type = st.selectbox(
            "Incident Type",
            ["Mechanical", "Electrical", "Injury", "Security"]
        )

        severity = st.selectbox(
            "Severity Level",
            ["Low", "Medium", "High", "Critical"]
        )

        description = st.text_area("Incident Description")
        action_taken = st.text_area("Immediate Action Taken")

        if st.button("Submit Incident"):
            insert_incident((
                terminal,
                incident_type,
                severity,
                description,
                action_taken,
                str(datetime.datetime.now())
            ))

            st.success("✅ Incident Recorded Successfully")

    # =====================================
    # ADMIN PANEL
    # =====================================
    elif st.session_state.role == "Admin":

        st.subheader("📊 All Incidents")

        incidents = get_all_incidents()

        if incidents:

            df = pd.DataFrame(incidents, columns=[
                "ID",
                "Terminal",
                "Incident Type",
                "Severity",
                "Description",
                "Action Taken",
                "Date"
            ])

            # Optional filter
            terminal_filter = st.selectbox(
                "Filter by Terminal",
                ["All"] + list(df["Terminal"].unique())
            )

            if terminal_filter != "All":
                df = df[df["Terminal"] == terminal_filter]

            # Display table
            st.subheader("📋 Incident Reports")

            for _, row in df.iterrows():

                # Severity color styling
                if row["Severity"] == "Critical":
                    severity_color = "red"
                elif row["Severity"] == "High":
                    severity_color = "orange"
                elif row["Severity"] == "Medium":
                    severity_color = "blue"
                else:
                    severity_color = "green"

                st.markdown(f"""
                ---
                ### 🏢 {row["Terminal"]}

                **🛠 Incident Type:** {row["Incident Type"]}  
                **⚠ Severity:** <span style='color:{severity_color}; font-weight:bold;'>{row["Severity"]}</span>  
                **🕒 Date:** {row["Date"]}

                **📝 Description:**  
                {row["Description"]}

                **✅ Action Taken:**  
                {row["Action Taken"]}
                """, unsafe_allow_html=True)


            st.markdown("---")

            # Simple statistics
            col1, col2, col3 = st.columns(3)

            col1.metric("Total Incidents", len(df))
            col2.metric("High Severity", len(df[df["Severity"] == "High"]))
            col3.metric("Critical", len(df[df["Severity"] == "Critical"]))

            st.markdown("---")

            # AI Analysis
            if st.button("🤖 Run AI Safety Analysis"):
                with st.spinner("Analyzing incidents..."):
                    result = analyze_incidents(incidents)

                st.subheader("🧠 AI Safety Insights")
                st.write(result)

        else:
            st.info("No incidents recorded yet.")
