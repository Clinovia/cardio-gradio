# ui/templates.py

"""
UI Templates
------------
This module defines reusable text templates and message snippets
for the chatbot interface.
"""

WELCOME_MESSAGE = """
Welcome to the Health AI Assistant! 🤖
I can help you with risk assessments, medical information, and more.
Please note: I am not a substitute for professional medical advice.
"""

INSTRUCTIONS_MESSAGE = """
You can:
- Upload medical images or health data.
- Ask questions about Alzheimer's, cardiology, and more.
- Get preliminary screening suggestions.

⚠ Always consult a licensed healthcare professional before making decisions.
"""

ERROR_MESSAGE = """
⚠ Oops! Something went wrong.
Please try again, or contact support if the issue persists.
"""

RESULTS_TEMPLATE = """
📊 **{condition} Risk Assessment**
- Risk Score: **{score:.2f}**
- Assessment: {assessment}
- Recommendation: {recommendation}
"""

CONFIRMATION_TEMPLATE = """
✅ Your data has been processed successfully.
"""

GOODBYE_MESSAGE = """
Thank you for using Health AI Assistant. Stay healthy! 🌿
"""

def get_results_message(condition, score, assessment, recommendation):
    """Formats the results template with provided data."""
    return RESULTS_TEMPLATE.format(
        condition=condition,
        score=score,
        assessment=assessment,
        recommendation=recommendation
    )
