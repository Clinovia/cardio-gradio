# cardio_app.py
import gradio as gr
from calculators.ascvd import ascvd
from calculators.bp_category import bp_category
from calculators.cha2ds2vasc import cha2ds2vasc
from calculators.ecg_interpret import (
    interpret_rhythm,
    interpret_12lead_findings,
    interpret_ecg_comprehensive,
)
from validators.patient_input import (
    validate_ascvd_input,
    validate_bp_input,
    validate_cha2ds2vasc_input,
    validate_ecg_rhythm_input,
    validate_ecg_12lead_input,
)
import logging
import uuid

# -----------------------------
# Logger setup
# -----------------------------
logging.basicConfig(
    filename="usage.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

def log_usage(tool_name, inputs, outputs=None):
    session_id = str(uuid.uuid4())[:8]
    logging.info(
        f"session={session_id} tool={tool_name} inputs={inputs} outputs={outputs}"
    )

# -----------------------------
# ASCVD Risk Calculator
# -----------------------------
def run_ascvd(age, sex, race, total_chol, hdl, sbp, on_htn_meds, smoker, diabetes, patient_id="N/A"):
    data = {
        "age": age,
        "sex": sex,
        "race": race,
        "total_cholesterol": total_chol,
        "hdl": hdl,
        "sbp": sbp,
        "on_htn_meds": on_htn_meds,
        "smoker": smoker,
        "diabetes": diabetes,
    }
    try:
        validate_ascvd_input(data)
        risk = ascvd(data)
        category = (
            "High" if risk >= 0.20 else
            "Intermediate" if risk >= 0.075 else
            "Borderline" if risk >= 0.05 else
            "Low"
        )
        result_text = f"10-Year ASCVD Risk: {risk:.1%} ({category})"
        log_usage("ascvd", data, result_text)
        return result_text
    except ValueError as e:
        log_usage("ascvd", data, f"Error: {str(e)}")
        return f"❌ Input Error: {str(e)}"

# -----------------------------
# Blood Pressure Category
# -----------------------------
def run_bp(sbp, dbp, patient_id="N/A"):
    data = {"sbp": sbp, "dbp": dbp}
    try:
        validate_bp_input(sbp, dbp)
        category = bp_category(sbp, dbp)
        result_text = f"Blood Pressure Category: {category}"
        log_usage("bp_category", data, result_text)
        return result_text
    except ValueError as e:
        log_usage("bp_category", data, f"Error: {str(e)}")
        return f"❌ Input Error: {str(e)}"

# -----------------------------
# CHA₂DS₂-VASc
# -----------------------------
def run_cha2ds2vasc(chf, htn, age75, diabetes, stroke, vascular, age65_74, female, patient_id="N/A"):
    data = {
        "chf": int(chf),
        "hypertension": int(htn),
        "age_ge_75": int(age75),
        "diabetes": int(diabetes),
        "stroke": int(stroke),
        "vascular": int(vascular),
        "age_65_74": int(age65_74),
        "female": int(female),
    }
    try:
        validate_cha2ds2vasc_input(data)
        score = cha2ds2vasc(data)
        result_text = f"CHA₂DS₂-VASc Score: {score}"
        log_usage("cha2ds2vasc", data, result_text)
        return result_text
    except ValueError as e:
        log_usage("cha2ds2vasc", data, f"Error: {str(e)}")
        return f"❌ Input Error: {str(e)}"

# -----------------------------
# ECG Interpretation
# -----------------------------
def run_ecg(rate, regular, p_waves_present, st_elev, st_elev_leads, qt, rr, lvh, q_waves, q_leads, t_inversion, pr, patient_id="N/A"):
    rhythm_data = {"rate": rate, "regular": regular, "p_waves_present": p_waves_present}
    lead_data = {
        "st_elevation": st_elev,
        **({"st_elevation_leads": st_elev_leads} if st_elev and st_elev_leads else {}),
        "qt_interval_ms": qt,
        "rr_interval_ms": rr,
        "lvh_criteria_met": lvh,
        "pathological_q_waves": q_waves,
        **({"q_wave_leads": q_leads} if q_waves and q_leads else {}),
        "t_wave_inversion": t_inversion,
        "pr_interval_ms": pr,
    }
    try:
        validate_ecg_rhythm_input(rhythm_data)
        validate_ecg_12lead_input(lead_data)

        rhythm = interpret_rhythm(rate, regular, p_waves_present)
        findings = interpret_12lead_findings(lead_data)
        comprehensive = interpret_ecg_comprehensive({**rhythm_data, **lead_data})

        # Format findings for user-friendly output
        findings_text = findings["findings"]
        if not findings_text:
            findings_text = "No 12-lead abnormalities detected"

        summary = (
            f"Rhythm: {rhythm}\n"
            f"Findings: {findings_text}\n"
            f"Overall Risk: {comprehensive['overall_risk']}"
        )

        log_usage("ecg_interpret", {**rhythm_data, **lead_data}, summary)

        return summary
    except ValueError as e:
        log_usage("ecg_interpret", {**rhythm_data, **lead_data}, f"Error: {str(e)}")
        return f"❌ Input Error: {str(e)}"

# -----------------------------
# Gradio UI
# -----------------------------
with gr.Blocks(title="Cardio-Tool (RUO)") as demo:
    gr.Markdown("## ⚠️ Cardio-Tool — Research Use Only\nNot for clinical diagnosis.")

    with gr.Tabs():
        with gr.TabItem("ASCVD Risk"):
            age = gr.Slider(40, 79, value=60, label="Age")
            sex = gr.Dropdown(["Male", "Female"], label="Sex")
            race = gr.Dropdown(["White", "Black"], label="Race")
            total_chol = gr.Slider(100, 400, value=200, label="Total Cholesterol (mg/dL)")
            hdl = gr.Slider(20, 100, value=50, label="HDL (mg/dL)")
            sbp = gr.Slider(70, 250, value=120, label="Systolic BP (mmHg)")
            htn = gr.Checkbox(label="On HTN Meds?")
            smoker = gr.Checkbox(label="Smoker?")
            diabetes = gr.Checkbox(label="Diabetes?")
            patient_id = gr.Textbox(label="Patient ID", placeholder="Optional")
            out_text = gr.Textbox(label="Result")
            btn = gr.Button("Calculate ASCVD Risk")
            btn.click(run_ascvd,
                      [age, sex, race, total_chol, hdl, sbp, htn, smoker, diabetes, patient_id],
                      out_text)

        with gr.TabItem("Blood Pressure"):
            sbp2 = gr.Slider(50, 250, value=120, label="Systolic BP (mmHg)")
            dbp2 = gr.Slider(40, 150, value=80, label="Diastolic BP (mmHg)")
            patient_id2 = gr.Textbox(label="Patient ID", placeholder="Optional")
            out_text2 = gr.Textbox(label="Result")
            btn2 = gr.Button("Classify BP")
            btn2.click(run_bp, [sbp2, dbp2, patient_id2], out_text2)

        with gr.TabItem("CHA2DS2-VASc"):
            chf = gr.Checkbox(label="CHF")
            htn_cb = gr.Checkbox(label="Hypertension")
            age75 = gr.Checkbox(label="Age ≥75")
            diabetes2 = gr.Checkbox(label="Diabetes")
            stroke = gr.Checkbox(label="Stroke/TIA/Thromboembolism")
            vascular = gr.Checkbox(label="Vascular Disease")
            age65 = gr.Checkbox(label="Age 65–74")
            female_cb = gr.Checkbox(label="Female")
            patient_id3 = gr.Textbox(label="Patient ID", placeholder="Optional")
            out_text3 = gr.Textbox(label="Result")
            btn3 = gr.Button("Calculate CHA2DS2-VASc")
            btn3.click(run_cha2ds2vasc,
                       [chf, htn_cb, age75, diabetes2, stroke, vascular, age65, female_cb, patient_id3],
                       out_text3)

        with gr.TabItem("ECG Interpretation"):
            rate = gr.Slider(20, 250, value=75, label="Heart Rate (bpm)")
            regular = gr.Checkbox(label="Rhythm Regular?")
            p_waves = gr.Checkbox(label="P Waves Present?")
            st_elev = gr.Checkbox(label="ST Elevation?")
            st_elev_leads = gr.Textbox(label="ST Elevation Leads")
            qt = gr.Slider(300, 700, value=400, label="QT Interval (ms)")
            rr = gr.Slider(300, 1200, value=800, label="RR Interval (ms)")
            lvh = gr.Checkbox(label="LVH Criteria Met?")
            q_waves = gr.Checkbox(label="Pathological Q Waves?")
            q_leads = gr.Textbox(label="Q Wave Leads")
            t_inv = gr.Checkbox(label="T-Wave Inversion?")
            pr = gr.Slider(120, 300, value=160, label="PR Interval (ms)")
            patient_id4 = gr.Textbox(label="Patient ID", placeholder="Optional")
            out_text4 = gr.Textbox(label="Result", lines=4)
            btn4 = gr.Button("Interpret ECG")
            btn4.click(run_ecg,
                       [rate, regular, p_waves, st_elev, st_elev_leads, qt, rr, lvh, q_waves, q_leads, t_inv, pr, patient_id4],
                       out_text4)

demo.launch(debug=True, share=True)
