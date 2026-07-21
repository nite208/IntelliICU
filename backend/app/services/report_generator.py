"""
Clinical Report Generator Service.
Integrates context builders, explainable AI, and RAG to generate structured notes and PDFs.
"""

import io
import uuid
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.services.context_builder import PatientContextBuilder
from app.services.clinical_copilot_service import ClinicalCopilotService

# In-memory database to store generated reports (no DB migrations)
REPORTS_DB: Dict[str, Dict[str, Any]] = {}

class ClinicalReportGenerator:
    """
    Generates and stores ICU Progress Notes, Daily Clinical Summaries, Handover notes, and PDFs.
    """

    def __init__(self):
        self.context_builder = PatientContextBuilder()
        self.copilot_service = ClinicalCopilotService()

    def generate_report(self, patient_id: str, report_type: str) -> Dict[str, Any]:
        # 1. Fetch full patient context
        context = self.context_builder.build_context(patient_id)
        if not context or "patient" not in context:
            raise ValueError(f"Patient context not found for ID: {patient_id}")

        patient_name = context["patient"]["name"]

        # 2. Formulate query based on report type to get AI reasoning
        queries = {
            "ICU Progress Note": "Provide a comprehensive ICU progress note, evaluating vitals trends, abnormal labs, and priority recommendations.",
            "Daily Clinical Summary": "Explain daily clinical status, sepsis risk drivers, and active telemetry alerts.",
            "Shift Handover": "Give shift handover highlights, vital signs summary, and primary stabilization recommendations.",
            "Discharge Summary": "Provide a discharge summary, evaluating stable baselines, resolved alerts, and follow-up care recommendations."
        }
        query = queries.get(report_type, f"Summarize patient status for {report_type}.")

        # 3. Query Clinical Copilot (uses RAG and Explainable AI)
        ai_response = self.copilot_service.get_answer(patient_id, query)

        # Extract AI parameters
        ai_reasoning = ai_response.get("reasoning") or ai_response.get("answer") or ai_response.get("summary") or ""
        recommendations = ai_response.get("recommendations") or []
        evidence = ai_response.get("evidence") or []
        confidence = ai_response.get("confidence") or 0.90

        # 4. Construct structured note content JSON
        report_id = f"rep-{uuid.uuid4().hex[:8]}"
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report_content = {
            "demographics": context.get("patient") or {},
            "admission": context.get("admission") or {},
            "vitals": context.get("vitals") or {},
            "vital_trends": context.get("vital_trends") or {},
            "labs": context.get("labs") or {},
            "abnormal_labs": context.get("abnormal_labs") or [],
            "active_alerts": context.get("alerts") or [],
            "medications": context.get("medications") or [],
            "clinical_priority": context.get("clinical_priority") or "MEDIUM",
            "ai_reasoning": ai_reasoning,
            "clinical_recommendations": recommendations,
            "guideline_evidence": evidence,
            "confidence": confidence
        }

        report = {
            "report_id": report_id,
            "patient_id": patient_id,
            "patient_name": patient_name,
            "report_type": report_type,
            "created_at": created_at,
            "content": report_content
        }

        # 5. Store in-memory
        REPORTS_DB[report_id] = report

        return report

    def get_report(self, report_id: str) -> Dict[str, Any] | None:
        return REPORTS_DB.get(report_id)

    def generate_pdf_bytes(self, report_id: str) -> bytes:
        report = self.get_report(report_id)
        if not report:
            raise ValueError(f"Report not found for ID: {report_id}")

        content = report["content"]
        patient_name = report["patient_name"]
        patient_id = report["patient_id"]
        report_type = report["report_type"]
        created_at = report["created_at"]

        # Initialize ReportLab canvas
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Colors matching IntelliICU branding
        PRIMARY_COLOR = (7/255, 35/255, 63/255) # #07233f Dark Navy
        ACCENT_COLOR = (2/255, 132/255, 199/255) # #0284c7 Clinical Blue
        TEXT_COLOR = (30/255, 41/255, 59/255) # Slate-800
        MUTED_TEXT = (100/255, 116/255, 139/255) # Slate-500

        # Helper to wrap text
        def draw_string_wrapped(text_str: str, x: float, y: float, max_w: float, line_h: float = 14) -> float:
            words = text_str.split()
            lines = []
            curr_line = []
            for word in words:
                test_line = " ".join(curr_line + [word])
                if p.stringWidth(test_line) < max_w:
                    curr_line.append(word)
                else:
                    lines.append(" ".join(curr_line))
                    curr_line = [word]
            if curr_line:
                lines.append(" ".join(curr_line))

            for line in lines:
                if y < 50:
                    p.showPage()
                    draw_page_template()
                    y = height - 80
                p.drawString(x, y, line)
                y -= line_h
            return y

        # Helper to draw footer & header templates
        def draw_page_template():
            p.setStrokeColorRGB(*PRIMARY_COLOR)
            p.setLineWidth(1)
            p.line(40, height - 40, width - 40, height - 40)
            
            p.setFont("Helvetica-Bold", 8)
            p.setFillColorRGB(*MUTED_TEXT)
            p.drawString(40, height - 35, "INTELLIICU CLINICAL REPORT SUITE")
            p.drawRightString(width - 40, height - 35, f"REPORT: {report_id.upper()}")

            p.line(40, 45, width - 40, 45)
            p.drawString(40, 32, "Confidential Medical Document - Generated by AI Clinical Assistant")
            p.drawRightString(width - 40, 32, f"Page {p.getPageNumber()}")

        # Page 1 Setup
        draw_page_template()

        # Document Header
        p.setFont("Helvetica-Bold", 20)
        p.setFillColorRGB(*PRIMARY_COLOR)
        p.drawString(40, height - 70, report_type.upper())

        p.setFont("Helvetica", 9)
        p.setFillColorRGB(*MUTED_TEXT)
        p.drawString(40, height - 85, f"Date: {created_at} | Priority: {content.get('clinical_priority', 'MEDIUM')}")

        # Demographics Card
        y = height - 100
        p.setFillColorRGB(248/255, 250/255, 252/255) # Light background
        p.rect(40, y - 60, width - 80, 50, fill=True, stroke=False)
        
        p.setFont("Helvetica-Bold", 10)
        p.setFillColorRGB(*PRIMARY_COLOR)
        p.drawString(50, y - 25, "PATIENT PROFILE")
        
        p.setFont("Helvetica", 9)
        p.setFillColorRGB(*TEXT_COLOR)
        demo_str = f"Name: {patient_name}  |  Age/Sex: {content['demographics'].get('age')}yo {content['demographics'].get('gender')}  |  Patient ID: {patient_id}"
        p.drawString(50, y - 40, demo_str)
        
        adm_str = f"Diagnosis: {content['admission'].get('diagnosis', 'N/A')}  |  Bed: {content['admission'].get('bed_number', 'N/A')}  |  Physician: {content['admission'].get('doctor_name', 'N/A')}"
        p.drawString(50, y - 52, adm_str)

        # AI Reasoning Summary
        y -= 85
        p.setFont("Helvetica-Bold", 11)
        p.setFillColorRGB(*PRIMARY_COLOR)
        p.drawString(40, y, "AI CLINICAL REASONING SUMMARY")
        p.line(40, y - 4, width - 40, y - 4)

        y -= 18
        p.setFont("Helvetica", 9.5)
        p.setFillColorRGB(*TEXT_COLOR)
        y = draw_string_wrapped(content.get("ai_reasoning", "No summary notes generated."), 40, y, width - 80, 14)

        # Vitals & Trends
        y -= 20
        p.setFont("Helvetica-Bold", 11)
        p.setFillColorRGB(*PRIMARY_COLOR)
        p.drawString(40, y, "PHYSIOLOGICAL VITAL TRENDS")
        p.line(40, y - 4, width - 40, y - 4)

        y -= 20
        p.setFont("Helvetica", 9.5)
        p.setFillColorRGB(*TEXT_COLOR)
        v = content.get("vitals") or {}
        trends = content.get("vital_trends") or {}
        
        v_lines = [
            f"Heart Rate: {v.get('heart_rate')} bpm (Trend: {trends.get('heart_rate', {}).get('direction', 'stable')})",
            f"Blood Pressure: {v.get('systolic_bp')}/{v.get('diastolic_bp')} mmHg (Trend: {trends.get('systolic_bp', {}).get('direction', 'stable')})",
            f"Oxygen Saturation (SpO2): {v.get('spo2')}% (Trend: {trends.get('spo2', {}).get('direction', 'stable')})",
            f"Temperature: {v.get('temperature')}°C (Trend: {trends.get('temperature', {}).get('direction', 'stable')})"
        ]
        
        for line in v_lines:
            p.drawString(50, y, f"- {line}")
            y -= 14

        # Abnormal Labs
        y -= 15
        p.setFont("Helvetica-Bold", 11)
        p.setFillColorRGB(*PRIMARY_COLOR)
        p.drawString(40, y, "ABNORMAL LAB DRAW METRICS")
        p.line(40, y - 4, width - 40, y - 4)

        y -= 20
        ab_labs = content.get("abnormal_labs") or []
        if ab_labs:
            for lab in ab_labs:
                if y < 60:
                    p.showPage()
                    draw_page_template()
                    y = height - 80
                p.setFont("Helvetica-Bold", 9.5)
                p.setFillColorRGB(*TEXT_COLOR)
                p.drawString(50, y, f"{lab['metric']}: {lab['value']}")
                p.setFont("Helvetica", 9)
                p.drawString(180, y, f"(Normal Range: {lab['reference']})")
                p.drawRightString(width - 50, y, f"{lab['status']} [{lab['severity']}]")
                y -= 14
        else:
            p.setFont("Helvetica-Oblique", 9)
            p.drawString(50, y, "All standard chemistry values within normal reference limits.")
            y -= 14

        # Active Alerts
        y -= 15
        if y < 80:
            p.showPage()
            draw_page_template()
            y = height - 80
        p.setFont("Helvetica-Bold", 11)
        p.setFillColorRGB(*PRIMARY_COLOR)
        p.drawString(40, y, "ACTIVE CLINICAL TELEMETRY ALARMS")
        p.line(40, y - 4, width - 40, y - 4)

        y -= 20
        alerts = content.get("active_alerts") or []
        if alerts:
            for alert in alerts:
                if y < 60:
                    p.showPage()
                    draw_page_template()
                    y = height - 80
                p.setFont("Helvetica-Bold", 9.5)
                p.drawString(50, y, f"[{alert['severity']}] {alert['title']}")
                p.setFont("Helvetica", 9)
                p.drawString(200, y, alert['message'])
                y -= 14
        else:
            p.setFont("Helvetica-Oblique", 9)
            p.drawString(50, y, "No active alerts registered.")
            y -= 14

        # Recommendations & Evidence
        y -= 15
        if y < 100:
            p.showPage()
            draw_page_template()
            y = height - 80
        p.setFont("Helvetica-Bold", 11)
        p.setFillColorRGB(*PRIMARY_COLOR)
        p.drawString(40, y, "CLINICAL RECOMMENDATIONS & PATHWAYS")
        p.line(40, y - 4, width - 40, y - 4)

        y -= 20
        recs = content.get("clinical_recommendations") or []
        for rec in recs:
            p.setFont("Helvetica", 9.5)
            y = draw_string_wrapped(f"- {rec}", 50, y, width - 90, 14)

        # Saved
        p.save()
        return buffer.getvalue()
