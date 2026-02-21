from openai import OpenAI
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


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
        return "❌ GROQ_API_KEY not found in .env file."

    try:
        # Create Groq-compatible OpenAI client
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )

        if not incidents:
            return "No incidents recorded."

        formatted_data = "\n".join([
            f"Terminal: {row[1]} | Type: {row[2]} | Severity: {row[3]} | Description: {row[4]}"
            for row in incidents
        ])

        prompt = f"""
You are a professional marine safety analyst.

Analyze the following incident dataset.

Provide:
1. Terminal risk ranking
2. Recurring patterns
3. Severity distribution insight
4. Root cause hypothesis
5. Operational risk level
6. Clear actionable recommendations

Dataset:
{formatted_data}
"""

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # Use this smaller model first (more stable)
            messages=[
                {"role": "system", "content": "You are an expert safety operations analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Groq API Error:\n\n{str(e)}"
