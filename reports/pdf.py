# reports/pdf.py
from fpdf import FPDF

def create_pdf_report(data: dict, title: str, return_base64=False):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, title, ln=True)

    pdf.set_font("Arial", '', 12)
    for key, value in data.items():
        pdf.ln(8)
        pdf.cell(0, 10, f"{key}: {value}", ln=True)

    if return_base64:
        import base64
        import io
        buf = io.BytesIO()
        pdf.output(buf)
        return base64.b64encode(buf.getvalue()).decode()
    else:
        import io
        buf = io.BytesIO()
        pdf.output(buf)
        return buf.getvalue()
