"""
Context Optimizer Service.
Reduces full Patient Clinical Context to a concise summary for local LLM inference.
"""

from typing import Dict, Any

class ContextOptimizer:
    """
    Optimizes comprehensive clinical contexts for LLM consumption by truncating history
    and keeping only essential parameters.
    """

    @staticmethod
    def optimize(context: Dict[str, Any]) -> Dict[str, Any]:
        patient = context.get("patient", {})
        admission = context.get("admission", {})
        vitals = context.get("vitals", {})
        vital_trends = context.get("vital_trends", {})
        
        # Format vital trends simply
        trends_summary = {}
        if isinstance(vital_trends, dict):
            for metric, data in vital_trends.items():
                if isinstance(data, dict) and "direction" in data:
                    trends_summary[metric] = f"{data['direction']} (last: {data.get('last_value', '-')}, prev: {data.get('previous_value', '-')})"

        # Keep abnormal labs condensed
        abnormal_labs = []
        for lab in context.get("abnormal_labs", []):
            if isinstance(lab, dict):
                abnormal_labs.append(f"{lab.get('metric')}: {lab.get('value')} ({lab.get('status')})")

        # Keep active alerts condensed
        active_alerts = []
        for alert in context.get("alerts", []):
            if isinstance(alert, dict) and alert.get("status") == "ACTIVE":
                active_alerts.append(f"{alert.get('title')}: {alert.get('message')} ({alert.get('severity')})")

        optimized = {
            "patient": {
                "id": patient.get("id"),
                "name": patient.get("name"),
                "age": patient.get("age"),
                "gender": patient.get("gender")
            },
            "admission": {
                "diagnosis": admission.get("diagnosis"),
                "ward": admission.get("ward"),
                "bed_number": admission.get("bed_number")
            },
            "latest_vitals": {
                "heart_rate": vitals.get("heart_rate"),
                "spo2": vitals.get("spo2"),
                "temperature": vitals.get("temperature"),
                "systolic_bp": vitals.get("systolic_bp") or vitals.get("blood_pressure", {}).get("systolic"),
                "diastolic_bp": vitals.get("diastolic_bp") or vitals.get("blood_pressure", {}).get("diastolic"),
                "respiratory_rate": vitals.get("respiratory_rate")
            },
            "vital_trends_summary": trends_summary,
            "latest_abnormal_labs": abnormal_labs,
            "active_medications": context.get("medications", []),
            "active_alerts": active_alerts,
            "ai_risk_score": context.get("risk_level") or patient.get("risk_score"),
            "clinical_priority": context.get("clinical_priority")
        }
        return optimized
