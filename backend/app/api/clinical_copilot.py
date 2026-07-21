"""
Clinical Copilot Router.
Exposes endpoints for chat reasoning, patient context inquiries, and clinical report generation.
"""

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import StreamingResponse
from app.schemas.clinical_chat import ClinicalChatRequest, ClinicalChatResponse
from app.schemas.clinical_report import ClinicalReportRequest, ClinicalReportResponse
from app.services.clinical_copilot_service import ClinicalCopilotService
from app.services.report_generator import ClinicalReportGenerator

router = APIRouter(
    prefix="/clinical-copilot",
    tags=["Clinical Copilot"],
)

service = ClinicalCopilotService()
report_generator = ClinicalReportGenerator()

@router.post(
    "/chat",
    summary="Clinical Copilot Chat Agent",
    description="Analyze patient records and run reasoning based on the prompt/question, supporting SSE streaming."
)
def chat_endpoint(request: ClinicalChatRequest, stream: bool = False):
    """
    Handle POST queries for clinical copilot reasoning.
    Returns JSON payload or streams Server-Sent Events (SSE).
    """
    if stream:
        generator = service.get_streaming_answer(
            patient_id=request.patient_id,
            question=request.question,
        )
        return StreamingResponse(generator, media_type="text/event-stream")
    else:
        result = service.get_answer(
            patient_id=request.patient_id,
            question=request.question,
        )
        return result

@router.post(
    "/report",
    response_model=ClinicalReportResponse,
    summary="Generate Clinical Report",
    description="Generate a progress note, daily summary, shift handover, or discharge note."
)
def create_report(request: ClinicalReportRequest):
    """
    Generate structured notes using patient clinical context and RAG guidelines.
    """
    try:
        result = report_generator.generate_report(
            patient_id=request.patient_id,
            report_type=request.report_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get(
    "/report/{report_id}",
    response_model=ClinicalReportResponse,
    summary="Retrieve Clinical Report",
    description="Retrieve a stored in-memory report."
)
def get_report(report_id: str):
    """
    Retrieve stored report structures.
    """
    report = report_generator.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get(
    "/report/{report_id}/pdf",
    summary="Download PDF Clinical Report",
    description="Returns a professional, styled ReportLab PDF binary."
)
def download_pdf(report_id: str):
    """
    Generate and stream ReportLab PDF outputs.
    """
    try:
        pdf_bytes = report_generator.generate_pdf_bytes(report_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=clinical_report_{report_id}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
