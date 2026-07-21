import time
from typing import Dict, Any, Generator
from app.ai.providers.base import BaseLLMProvider
from app.services.explainable_reasoning_service import ExplainableReasoningService

class MockLLMProvider(BaseLLMProvider):
    """
    Simulates clinical LLM responses by delegating to ExplainableReasoningService
    or building dynamic hospital snapshots if conversational context is requested.
    """

    def generate(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        snapshot = context.get("snapshot")
        if not snapshot and "conversation_history" in context:
            # Fallback to parsing history system message if snapshot dict not passed
            for msg in context["conversation_history"]:
                if msg.get("role") == "system":
                    break

        if "conversation_history" in context or "vitals" not in context:
            # Hospital-level query - construct dynamic response from live snapshot
            if not snapshot:
                snapshot = {
                    "summary": {"total_patients": 4, "critical_patients": 1, "sepsis_suspects": 1},
                    "critical_patients": [],
                    "active_alerts": [],
                    "telemetry_insights": [],
                    "patients_ranked": []
                }

            q = question.lower()
            summary = snapshot.get("summary", {})
            critical = snapshot.get("critical_patients", [])
            alerts = snapshot.get("active_alerts", [])
            telemetry = snapshot.get("telemetry_insights", [])
            actions = snapshot.get("recommended_actions", [])

            # Check if this is a floating assistant question
            if "[role:" in q:
                role_part = q.split("]")[0].replace("[role:", "").strip()
                user_q = q.split("]")[-1].strip()
                
                title = f"IntelliAI {role_part.title()} Workspace Helper"
                reasoning = f"### {title}\n\n"
                
                # Check for clinical diagnosis attempts
                if any(k in user_q for k in ["diagnose", "diagnosis", "disease", "treat", "prescribe", "medication dose"]):
                    reasoning += (
                        "⚠️ **Notice: Clinical Boundaries**\n"
                        "As an operational workspace helper, I am not permitted to perform patient diagnosis or treatment recommendations. "
                        "Please use the dedicated **Clinical AI Copilot** located directly on the individual patient profile page for clinical decision support.\n"
                    )
                    return {
                        "reasoning": reasoning,
                        "summary": reasoning,
                        "risk_drivers": [],
                        "abnormal_vitals": [],
                        "abnormal_labs": [],
                        "recommendations": [],
                        "evidence": [],
                        "confidence": 1.0,
                        "findings": [],
                        "risk": "Low"
                    }
                
                # Handle topics
                if any(k in user_q for k in ["health", "system", "status"]):
                    reasoning += (
                        "**System Status Indicators**:\n"
                        "- **API Status**: Online (FastAPI Relays)\n"
                        "- **Database**: Connected (PostgreSQL)\n"
                        "- **ICU Telemetry**: Active (Streaming Live)\n\n"
                        "**Shortcuts**:\n"
                        "- Check the system log metrics on your Admin Dashboard."
                    )
                elif any(k in user_q for k in ["user", "account", "directory", "add"]):
                    reasoning += (
                        "**User Management & Directory help**:\n"
                        "- **Access**: Navigate to the User Directory using the sidebar link.\n"
                        "- **Actions**: Add new clinical accounts, assign roles (Doctor, Nurse, ICUManager, HospitalAdmin), and change status.\n"
                    )
                elif any(k in user_q for k in ["task", "checklist", "nursing duty"]):
                    reasoning += (
                        "**Clinical Tasks Checklist Workflow**:\n"
                        "- **Access**: Find the Clinical Tasks card on the Nursing Dashboard.\n"
                        "- **Completion**: Click the check icon next to tasks to record completion.\n"
                    )
                elif any(k in user_q for k in ["bed", "occupancy", "capacity"]):
                    reasoning += (
                        "**ICU Occupancy Metrics**:\n"
                        f"- Bed Occupancy Rate: **{summary.get('bed_occupancy_pct', 0)}%**\n"
                        f"- Beds Open: **{summary.get('available_beds', 0)} / {summary.get('icu_capacity', 10)}**\n\n"
                        "**Navigation**:\n"
                        "- Open the Operations Dashboard to check the live occupancy monitor."
                    )
                elif any(k in user_q for k in ["alert", "critical", "deterioration"]):
                    reasoning += (
                        "**Active ICU Alerts & Warnings**:\n"
                        f"- Alerts currently active: **{summary.get('active_alert_count', 0)}**\n"
                        f"- Patients at high risk: **{summary.get('critical_patients', 0)}**\n\n"
                        "**Actions**:\n"
                        "- Review active warnings in the **Live Alerts** dashboard timeline."
                    )
                else:
                    reasoning += f"Welcome to the IntelliAI helper context. Here are workflow shortcuts for your **{role_part.upper()}** profile:\n\n"
                    if "admin" in role_part:
                        reasoning += (
                            "- **Manage Accounts**: View the User Directory sidebar options.\n"
                            "- **System Health**: Audit live FastAPI / DB indicators on your dashboard."
                        )
                    elif "doctor" in role_part:
                        reasoning += (
                            "- **Clinical AI**: Patient profile -> Clinical Copilot tab.\n"
                            "- **Hospital AI**: Open the 'Hospital AI' page in the sidebar for aggregate summaries."
                        )
                    elif "nurse" in role_part:
                        reasoning += (
                            "- **Nursing Workflow**: Access assigned beds and complete clinical tasks on your dashboard.\n"
                            "- **Vitals Monitor**: Check patient alerts dynamically."
                        )
                    else:
                        reasoning += (
                            "- **Unit Operations**: View Bed Occupancy grid and Analytics logs.\n"
                            "- **Performance**: Review average alert response statistics."
                        )
                
                return {
                    "reasoning": reasoning,
                    "summary": reasoning,
                    "risk_drivers": [],
                    "abnormal_vitals": [],
                    "abnormal_labs": [],
                    "recommendations": [],
                    "evidence": [],
                    "confidence": 1.0,
                    "findings": [],
                    "risk": "Low"
                }

            title = "ICU Status Report"
            reasoning = ""

            # Sepsis overview / sepsis suspects
            if "sepsis" in q:
                title = "Sepsis Overview & Suspects"
                sepsis_count = summary.get("sepsis_suspects", 0)
                reasoning = (
                    f"### {title}\n\n"
                    f"**Current Sepsis Suspect Count**: {sepsis_count} patients\n\n"
                    "#### Sepsis Prediction & Protocol Status\n"
                )
                
                sepsis_patients = []
                for p in snapshot.get("patients_ranked", []):
                    lactate = p.get("lactate")
                    risk = p.get("risk_score", 0)
                    if (lactate and lactate > 4.0) or risk > 0.80:
                        sepsis_patients.append(p)
                
                if sepsis_patients:
                    reasoning += "| Patient ID | Name | Bed | Sepsis Risk | Lactate (mmol/L) | Status |\n"
                    reasoning += "|---|---|---|---|---|---|\n"
                    for p in sepsis_patients:
                        reasoning += f"| `{p.get('id')}` | {p.get('name')} | {p.get('bed')} | {int(p.get('risk_score', 0)*100)}% | {p.get('lactate', 'N/A')} | {p.get('status')} |\n"
                    reasoning += "\n"
                else:
                    reasoning += "*No active sepsis suspects identified under current telemetry constraints.*\n\n"
                    
                reasoning += (
                    "#### Priorities & Recommendations\n"
                    "1. **Broad-Spectrum Antibiotics**: Initiate protocol within 1 hour for high-risk targets.\n"
                    "2. **Fluid Resuscitation**: Order 30mL/kg crystalloid for patients with lactate > 4.0.\n"
                    "3. **Frequent Monitoring**: Repeat lactate level checks every 2-4 hours.\n"
                )

            # Worsening trends
            elif "trend" in q or "worsening" in q:
                title = "Patients with Worsening Vital Trends"
                reasoning = (
                    f"### {title}\n\n"
                    f"**Worsening Telemetry Trends**: {summary.get('worsening_trend_count', 0)} patients affected\n\n"
                    "#### Active Telemetry Deteriorations\n"
                )
                
                if telemetry:
                    for t in telemetry:
                        reasoning += f"- **Patient {t.get('patient_name')} ({t.get('patient_id')})** in Bed **{t.get('bed')}**:\n"
                        reasoning += f"  - Vital Alerts: {', '.join(t.get('indicators', []))}\n"
                        reasoning += f"  - Direction: {t.get('trend_direction', 'Deteriorating')}\n"
                else:
                    reasoning += "*No significant vital signs deterioration detected across active beds.*\n\n"
                    
                reasoning += (
                    "\n#### Operational Actions\n"
                    "- **Telemetry Calibration**: Verify sensor connectivity on active alarms.\n"
                    "- **Nursing Notification**: Alert nurse of worsening respiratory and heart rate trends.\n"
                )

            # Bed occupancy / occupancy / utilization / ICU summary
            elif "bed" in q or "utilization" in q or "occupancy" in q or "summary" in q:
                title = "ICU Bed Utilization & Operations Summary"
                reasoning = (
                    f"### {title}\n\n"
                    f"**ICU Bed Occupancy**: {summary.get('bed_occupancy_pct', 0)}%\n"
                    f"**Available Beds**: {summary.get('available_beds', 0)} / {summary.get('icu_capacity', 10)}\n\n"
                    "#### Current Patient Distribution\n"
                    f"- **Critical**: {summary.get('critical_patients', 0)} patients\n"
                    f"- **Serious**: {summary.get('serious_patients', 0)} patients\n"
                    f"- **Stable**: {summary.get('stable_patients', 0)} patients\n\n"
                    "#### Active Clinical Alarm Load\n"
                    f"- **Active Alerts**: {summary.get('active_alert_count', 0)} warnings\n\n"
                    "#### Facility Recommendations\n"
                    "- **Discharge Planning**: Review stable patients for potential step-down transfers.\n"
                    "- **Admission Hold**: Keep 1 reserve bed open for emergency department escalations.\n"
                )

            # Lab values / abnormal labs
            elif "lab" in q or "laboratory" in q:
                title = "Patients with Abnormal Lab Interpretations"
                reasoning = (
                    f"### {title}\n\n"
                    "#### Key Critical Lab Markers\n"
                )
                
                abnormal_patients = []
                for p in snapshot.get("patients_ranked", []):
                    lactate = p.get("lactate")
                    if lactate and (lactate > 2.0):
                        abnormal_patients.append(p)
                
                if abnormal_patients:
                    reasoning += "| Patient ID | Name | Bed | Lactate (mmol/L) | Severity | Recommendation |\n"
                    reasoning += "|---|---|---|---|---|---|\n"
                    for p in abnormal_patients:
                        sev = "Critical" if p.get("lactate", 0) > 4.0 else "Elevated"
                        rec = "Check perfusion/sepsis" if sev == "Critical" else "Monitor trends"
                        reasoning += f"| `{p.get('id')}` | {p.get('name')} | {p.get('bed')} | {p.get('lactate')} | {sev} | {rec} |\n"
                    reasoning += "\n"
                else:
                    reasoning += "*No critical laboratory abnormalities detected in active census.*\n\n"
                    
                reasoning += (
                    "#### Lab Protocols\n"
                    "- **Verify Lactate**: Draw venous blood gas (VBG) for elevated lactates.\n"
                    "- **Culture Draws**: Draw blood cultures prior to launching antibiotic infusions.\n"
                )

            # Critical attention / high risk / default
            else:
                title = "Patients Requiring Immediate Attention / High Risk Overview"
                reasoning = (
                    f"### {title}\n\n"
                    f"**Critical Status Count**: {summary.get('critical_patients', 0)} high-risk ICU patients\n\n"
                    "#### High-Risk Patient Census\n"
                )
                
                if critical:
                    reasoning += "| Bed | Patient Name | Risk Score | Vital Status | Key Concern |\n"
                    reasoning += "|---|---|---|---|---|\n"
                    for p in critical:
                        concern = "Clinical Deterioration"
                        for a in alerts:
                            if a.get("patient_id") == p.get("id"):
                                concern = ", ".join(a.get("flags", []))
                                break
                        reasoning += f"| {p.get('bed')} | {p.get('name')} | {int(p.get('risk_score', 0)*100)}% | {p.get('status')} | {concern} |\n"
                    reasoning += "\n"
                else:
                    reasoning += "*No patients currently designated as high risk or critical status.*\n\n"

                if actions:
                    reasoning += "#### Recommended Priority Actions\n"
                    for idx, act in enumerate(actions[:3], 1):
                        reasoning += f"{idx}. **Bed {act.get('bed')}** ({act.get('patient_name')}): {act.get('action')} [Priority: {act.get('priority')}]\n"

            return {
                "reasoning": reasoning,
                "summary": reasoning,
                "risk_drivers": [p.get("name", "") for p in critical],
                "abnormal_vitals": [a.get("patient_name", "") for a in alerts],
                "abnormal_labs": [p.get("name", "") for p in snapshot.get("patients_ranked", []) if p.get("lactate", 0) > 2.0],
                "recommendations": [act.get("action", "") for act in actions],
                "evidence": ["Real-time monitor database scan"],
                "confidence": 0.98,
                "findings": ["Real-time telemetry scan"],
                "risk": "High" if len(critical) > 0 else "Low"
            }

        explanation = ExplainableReasoningService.process_explainable_query(question, context)
        # Populate legacy fields for backward compatibility
        explanation["summary"] = explanation["reasoning"]
        explanation["findings"] = explanation["risk_drivers"] + explanation["abnormal_vitals"] + explanation["abnormal_labs"]
        explanation["risk"] = explanation["risk_drivers"][0] if explanation["risk_drivers"] else "Unknown"
        return explanation

    def generate_stream(self, question: str, context: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Simulates word-by-word streaming of clinical reasoning.
        """
        final_response = self.generate(question, context)
        reasoning = final_response.get("reasoning", "")

        words = reasoning.split(" ")
        for word in words:
            yield {"type": "token", "content": word + " "}
            time.sleep(0.02)

        yield {"type": "final", "content": final_response}

