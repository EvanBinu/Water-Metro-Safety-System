import streamlit as st
from openai import OpenAI
from collections import Counter

# 1. Access the key correctly from Streamlit secrets
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

def local_analysis(incidents):
    if not incidents:
        return "No incidents recorded."

    terminals = [row[1] for row in incidents]
    types = [row[2] for row in incidents]
    severities = [row[3] for row in incidents]

    terminal_count = Counter(terminals)
    type_count = Counter(types)
    severity_count = Counter(severities)

    report = "📊 Local Safety Analysis (Fallback Mode)\n\n"
    report += f"Most Affected Terminal: {terminal_count.most_common(1)[0][0]}\n"
    report += f"Most Common Issue: {type_count.most_common(1)[0][0]}\n"
    report += f"High Severity Count: {severity_count.get('High', 0)}\n\n"
    report += "Recommendation: Increase inspection frequency at high-risk terminal."

    return report

def analyze_incidents(incidents):
    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY not found in Streamlit secrets."

    if not incidents:
        return "No incidents recorded."

    try:
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        # Better data formatting for the LLM to parse
        formatted_data = ""
        for i, row in enumerate(incidents, 1):
            formatted_data += f"{i}. [Terminal: {row[1]}] [Type: {row[2]}] [Severity: {row[3]}] - Obs: {row[4]}\n"

        # The Enhanced Prompt
        prompt = f"""
        # ROLE
        You are a Senior Marine Safety Auditor and Risk Management Expert. 

        # DATASET
        {formatted_data}

        # TASK
        Conduct a comprehensive safety audit based on the incident logs provided above. 
        Your goal is to identify systemic failures rather than just listing individual events.

        # RESPONSE REQUIREMENTS
        1. **Terminal Risk Matrix**: Rank terminals by risk (Critical > High > Medium).
        2. **Pattern Recognition**: Identify clusters (e.g., Are 'High' severity events happening at one specific terminal? Is one 'Type' of incident recurring?).
        3. **Severity Analysis**: Break down the distribution of severity levels.
        4. **Root Cause Hypothesis**: Use the '5 Whys' logic to suggest the likely underlying cause (e.g., infrastructure fatigue, training gaps, or environmental factors).
        5. **Operational Risk Level**: Assign an overall fleet safety score (Low, Elevated, High, or Immediate Action Required).
        6. **Actionable Mitigation Plan**: Provide 3 specific, prioritized steps to reduce future risk.

        # FORMATTING
        Use professional Markdown, bold key terms, and bullet points for readability.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "You provide high-level maritime safety intelligence and technical risk assessments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1, # Lowered for more consistent, analytical output
        )

        return response.choices[0].message.content

    except Exception as e:
        st.warning("Groq API failed. Providing local summary instead.")
        return f"{local_analysis(incidents)}\n\n(Error Detail: {str(e)})"

def get_safety_chatbot_response(user_query):
    """General purpose chatbot for workplace safety and security."""
    if not GROQ_API_KEY:
        return "❌ GROQ_API_KEY not found in Streamlit secrets."

    try:
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        system_prompt = """
        # ROLE
        You are a Work Site Safety & Security Advisor for the Kochi Water Metro. 
        Your expertise covers maritime security, electrical safety, passenger management, 
        emergency response, and OSHA-standard work site safety.

        # OBJECTIVE
        Answer general questions about safety protocols, security measures, and preventive 
        strategies. Be professional, concise, and prioritize human life above all.

        # GUIDELINES
        1. Provide accurate references to maritime standards (SOLAS, IMO) where applicable.
        2. Use bullet points for checklists or step-by-step instructions.
        3. If a user describes an active emergency, advise them to contact the command center immediately.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Sorry, I am having trouble connecting to the safety knowledge base. Error: {str(e)}"