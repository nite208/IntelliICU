"""
app/rag/nice.py

NICE (National Institute for Health and Care Excellence) detailed guidelines for Sepsis (NG51) and AKI (CG169).
"""

from app.rag.document import ClinicalDocument

DOCUMENTS = [
    ClinicalDocument(
        id="nice-sepsis-stratification-ng51",
        title="NICE NG51: Sepsis Risk Stratification in Adults",
        source="NICE Guideline NG51 2016 (updated 2024)",
        category="Sepsis",
        section="Risk Stratification",
        content=(
            "Stratify patients with suspected infection into high risk of severe illness or death "
            "based on the presence of: altered mental state, respiratory rate ≥25 breaths/min, "
            "new need for oxygen (FiO2 ≥40%), systolic blood pressure ≤90 mmHg (or relative drop >40 mmHg), "
            "heart rate >130 bpm, or mottled skin/cyanosis. High-risk patients mandate immediate "
            "broad-spectrum antibiotic administration and senior clinical review."
        ),
        tags=["sepsis", "risk", "stratification", "NICE", "blood pressure", "heart rate", "respiratory"],
    ),
    ClinicalDocument(
        id="nice-aki-detection-cg169",
        title="NICE CG169: Acute Kidney Injury Detection",
        source="NICE Guideline CG169 2013 (updated 2019)",
        category="AKI",
        section="Detection",
        content=(
            "Detect acute kidney injury in adults by monitoring serum creatinine and urine output. "
            "Use the following criteria: rise in serum creatinine of ≥26.5 micromol/L within 48 hours; "
            "or rise of ≥50% in serum creatinine known or presumed to have occurred within the past 7 days; "
            "or a fall in urine output to <0.5 mL/kg/h for more than 6 hours. Ensure baseline creatinine is "
            "sought from historical records."
        ),
        tags=["AKI", "detection", "creatinine", "urine output", "monitoring", "NICE"],
    ),
    ClinicalDocument(
        id="nice-intravenous-fluids-cg174",
        title="NICE CG174: Intravenous Fluid Therapy in Adults",
        source="NICE Guideline CG174 2013",
        category="Shock",
        section="Fluid Therapy",
        content=(
            "When prescribing intravenous fluids for resuscitation, use crystalloids that contain sodium "
            "in the range of 130-154 mmol/L (e.g., Hartmann's solution or balanced crystalloids) with a "
            "bolus of 250-500 mL over less than 15 minutes. Do not use tetrastarches for fluid resuscitation. "
            "Regularly assess fluid status using the 5 Rs: Resuscitation, Routine maintenance, Replacement, "
            "Redistribution, and Reassessment."
        ),
        tags=["shock", "fluids", "crystalloids", "resuscitation", "NICE", "balanced", "bolus"],
    ),
]
