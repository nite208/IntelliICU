"""
app/rag/kdigo.py

KDIGO (Kidney Disease: Improving Global Outcomes) detailed clinical guidelines for Acute Kidney Injury (AKI).
"""

from app.rag.document import ClinicalDocument

DOCUMENTS = [
    ClinicalDocument(
        id="kdigo-definition-staging-2012",
        title="KDIGO 2012: AKI Definition and Staging System",
        source="KDIGO Clinical Practice Guideline for AKI 2012",
        category="AKI",
        section="Definition and Staging",
        content=(
            "AKI is defined as any of the following: rise in serum creatinine by ≥0.3 mg/dL within 48 hours; "
            "or rise in serum creatinine to ≥1.5 times baseline, which is known or presumed to have occurred "
            "within the prior 7 days; or urine volume <0.5 mL/kg/h for 6 hours. AKI is staged from 1 to 3 "
            "based on the severity of serum creatinine elevation and the duration of oliguria."
        ),
        tags=["AKI", "definition", "staging", "creatinine", "oliguria", "urine output", "kidney"],
    ),
    ClinicalDocument(
        id="kdigo-prevention-fluids-2012",
        title="KDIGO 2012: Fluid Therapy and Hemodynamic Optimization",
        source="KDIGO Clinical Practice Guideline for AKI 2012",
        category="AKI",
        section="Prevention and Treatment",
        content=(
            "In the absence of hemorrhagic shock, we suggest using crystalloids rather than colloids "
            "(albumin or starches) for intravascular volume expansion in patients at risk of AKI or "
            "with AKI. We recommend against using hydroxyethyl starches (HES) for volume expansion "
            "due to increased risk of kidney injury and renal replacement therapy."
        ),
        tags=["AKI", "fluids", "crystalloids", "colloids", "starches", "volume expansion", "prevention"],
    ),
    ClinicalDocument(
        id="kdigo-nephrotoxin-stewardship-2012",
        title="KDIGO 2012: Nephrotoxic Medication Management",
        source="KDIGO Clinical Practice Guideline for AKI 2012",
        category="AKI",
        section="Prevention and Treatment",
        content=(
            "We recommend avoiding nephrotoxic medications when possible in patients at risk for AKI or "
            "with established AKI. Key nephrotoxins to monitor, adjust, or discontinue include NSAIDs, "
            "aminoglycosides, amphotericin B, calcineurin inhibitors, and glycopeptides. Contrast-induced "
            "AKI should be prevented using intravenous hydration with isotonic sodium bicarbonate or "
            "normal saline."
        ),
        tags=["AKI", "nephrotoxins", "medications", "contrast", "hydration", "NSAIDs", "aminoglycosides"],
    ),
    ClinicalDocument(
        id="kdigo-rrt-initiation-2012",
        title="KDIGO 2012: Timing of Renal Replacement Therapy",
        source="KDIGO Clinical Practice Guideline for AKI 2012",
        category="AKI",
        section="Renal Replacement Therapy",
        content=(
            "Initiate renal replacement therapy (RRT) urgently when life-threatening changes in fluid, "
            "electrolyte, and acid-base balance exist. Absolute indications include refractory hyperkalemia "
            "(K+ >6.5 mmol/L), severe metabolic acidosis (pH <7.1) driven by renal failure, fluid overload "
            "refractory to diuretics, and symptomatic uremia (e.g., pericarditis, encephalopathy)."
        ),
        tags=["AKI", "RRT", "dialysis", "hyperkalemia", "acidosis", "fluid overload", "uremia"],
    ),
]
