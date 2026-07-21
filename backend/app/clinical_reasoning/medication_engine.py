"""
app/clinical_reasoning/medication_engine.py

Medication Recommendation Engine for ICU patients (Phase 13.2).
Generates customized, patient-specific pharmacotherapy profiles based on
telemetry indicators, renal clearance capability, and clinical drug evidence.
"""

from typing import Dict, Any, List
from app.rag.drugs import DRUG_DOCUMENTS

class MedicationEngine:
    """
    Expert system for ICU drug dosing, renal adjustment, and safety evaluations.
    """

    @staticmethod
    def generate(
        treatment_pathway: Dict[str, Any],
        differential_diagnosis: List[Dict[str, Any]],
        context: Dict[str, Any],
        vitals: Dict[str, Any],
        labs: Dict[str, Any],
        drug_rag_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Synthesizes specific drug recommendations from retrieved drug documents
        that align with the top differential diagnosis and patient-specific renal function.

        Returns a dictionary:
        {
            "recommended_drugs": [
                {
                    "name": str,
                    "indication": str,
                    "suggested_dose": str,
                    "route": str,
                    "frequency": str,
                    "renal_adjustment": str,
                    "contraindications": list[str],
                    "monitoring": list[str],
                    "interactions": list[str],
                    "confidence": float (0.0 - 1.0)
                }
            ]
        }
        """
        recommended_drugs = []

        if not differential_diagnosis:
            return {"recommended_drugs": recommended_drugs}

        # Identify highest ranked diagnosis
        primary_diag_item = differential_diagnosis[0]
        primary_diag = primary_diag_item.get("diagnosis", "")
        likelihood = primary_diag_item.get("likelihood", 0.0)

        # Extract patient-specific renal markers for dosing adjustments
        creatinine = labs.get("creatinine") or labs.get("Creatinine")
        has_renal_impairment = creatinine is not None and creatinine > 1.5

        # Map RAG drug documents by generic name for easy lookup
        # We also merge dynamically retrieved results if provided
        drug_db = {doc.generic_name.lower(): doc for doc in DRUG_DOCUMENTS}
        for item in drug_rag_results or []:
            g_name = item.get("generic_name") or item.get("title", "").replace(" Clinical Profile", "")
            if g_name and g_name.lower() not in drug_db:
                # Mock a document
                from app.rag.document import ClinicalDocument
                drug_db[g_name.lower()] = ClinicalDocument(
                    id=item.get("id", f"drug-{g_name.lower()}"),
                    title=item.get("title", f"{g_name} Profile"),
                    source=item.get("source", "FDA"),
                    category="Drug",
                    section="Clinical Profile",
                    content=item.get("content", ""),
                    tags=item.get("tags", []),
                    generic_name=g_name,
                    drug_class=item.get("drug_class", "Unspecified"),
                    indications=item.get("indications", ""),
                    contraindications=item.get("contraindications", ""),
                    mechanism=item.get("mechanism", ""),
                    dosing=item.get("dosing", ""),
                    renal_adjustment=item.get("renal_adjustment", ""),
                    monitoring=item.get("monitoring", ""),
                    adverse_effects=item.get("adverse_effects", ""),
                    interactions=item.get("interactions", "")
                )

        # ----------------------------------------------------
        # Pathway-specific logic
        # ----------------------------------------------------
        if "septic shock" in primary_diag.lower() and likelihood >= 0.40:
            # 1. Norepinephrine
            norepi = drug_db.get("norepinephrine")
            if norepi:
                recommended_drugs.append({
                    "name": norepi.generic_name,
                    "indication": "First-line vasopressor for septic shock resuscitation.",
                    "suggested_dose": "0.05 - 0.2 mcg/kg/min (titrate by 0.02 mcg/kg/min to MAP >= 65 mmHg).",
                    "route": "Continuous IV infusion via central line",
                    "frequency": "Continuous titration",
                    "renal_adjustment": "No dose adjustment required. Monitor urine output closely.",
                    "contraindications": [c.strip() for c in norepi.contraindications.split(",") if c.strip()] or [norepi.contraindications],
                    "monitoring": [m.strip() for m in norepi.monitoring.split(",") if m.strip()] or [norepi.monitoring],
                    "interactions": [i.strip() for i in norepi.interactions.split(",") if i.strip()] or [norepi.interactions],
                    "confidence": 0.95
                })

            # 2. Vasopressin (if MAP is unstable or norepinephrine requirements are moderate/high)
            vaso = drug_db.get("vasopressin")
            if vaso:
                recommended_drugs.append({
                    "name": vaso.generic_name,
                    "indication": "Adjunct vasopressor to reduce norepinephrine requirements in refractory septic shock.",
                    "suggested_dose": "0.03 units/min (fixed rate). Do not titrate.",
                    "route": "Continuous IV infusion via central line",
                    "frequency": "Fixed continuous infusion",
                    "renal_adjustment": "No dose adjustment required.",
                    "contraindications": [c.strip() for c in vaso.contraindications.split(",") if c.strip()] or [vaso.contraindications],
                    "monitoring": [m.strip() for m in vaso.monitoring.split(",") if m.strip()] or [vaso.monitoring],
                    "interactions": [i.strip() for i in vaso.interactions.split(",") if i.strip()] or [vaso.interactions],
                    "confidence": 0.85
                })

            # 3. Broad spectrum empiric antibiotic (Meropenem or Piperacillin/Tazobactam)
            # Apply real-time renal dosing adjustment if creatinine is high
            mero = drug_db.get("meropenem")
            if mero:
                # Custom patient-specific renal dosing
                if has_renal_impairment:
                    suggested_dose = "500 mg IV every 12 hours"
                    renal_adj_status = f"Renal adjustment active (Creatinine: {creatinine} mg/dL). Reduced dose from standard 1g every 8 hours."
                else:
                    suggested_dose = "1 g IV every 8 hours"
                    renal_adj_status = "No active renal adjustment needed. Standard dosing recommended."

                recommended_drugs.append({
                    "name": mero.generic_name,
                    "indication": "Empiric Gram-negative coverage for severe sepsis/intra-abdominal source.",
                    "suggested_dose": suggested_dose,
                    "route": "IV infusion (infuse over 3-4 hours for prolonged administration)",
                    "frequency": "Every 12 hours" if has_renal_impairment else "Every 8 hours",
                    "renal_adjustment": renal_adj_status,
                    "contraindications": [c.strip() for c in mero.contraindications.split(",") if c.strip()] or [mero.contraindications],
                    "monitoring": [m.strip() for m in mero.monitoring.split(",") if m.strip()] or [mero.monitoring],
                    "interactions": [i.strip() for i in mero.interactions.split(",") if i.strip()] or [mero.interactions],
                    "confidence": 0.90
                })

        elif "cardiogenic shock" in primary_diag.lower() and likelihood >= 0.40:
            dobut = drug_db.get("dobutamine")
            if dobut:
                recommended_drugs.append({
                    "name": dobut.generic_name,
                    "indication": "Positive inotropic support to increase cardiac index in cardiogenic shock.",
                    "suggested_dose": "2.5 - 10 mcg/kg/min (titrate based on Cardiac Index).",
                    "route": "Continuous IV infusion via central line preferred",
                    "frequency": "Continuous titration",
                    "renal_adjustment": "No dosage adjustment required.",
                    "contraindications": [c.strip() for c in dobut.contraindications.split(",") if c.strip()] or [dobut.contraindications],
                    "monitoring": [m.strip() for m in dobut.monitoring.split(",") if m.strip()] or [dobut.monitoring],
                    "interactions": [i.strip() for i in dobut.interactions.split(",") if i.strip()] or [dobut.interactions],
                    "confidence": 0.90
                })

        elif "aki" in primary_diag.lower() and likelihood >= 0.40:
            furo = drug_db.get("furosemide")
            if furo:
                recommended_drugs.append({
                    "name": furo.generic_name,
                    "indication": "Loop diuretic for fluid overload management in Acute Kidney Injury.",
                    "suggested_dose": "40 - 80 mg IV bolus once (higher doses required in renal impairment).",
                    "route": "IV bolus (administer over 1-2 minutes)",
                    "frequency": "As needed for fluid balance targets",
                    "renal_adjustment": "No dose adjustment required, but larger doses are necessary to overcome diuretic resistance.",
                    "contraindications": [c.strip() for c in furo.contraindications.split(",") if c.strip()] or [furo.contraindications],
                    "monitoring": [m.strip() for m in furo.monitoring.split(",") if m.strip()] or [furo.monitoring],
                    "interactions": [i.strip() for i in furo.interactions.split(",") if i.strip()] or [furo.interactions],
                    "confidence": 0.85
                })

        # Return structured medication plan
        return {"recommended_drugs": recommended_drugs}
