"""
app/rag/sources.py

Seed clinical documents for the IntelliICU RAG knowledge base.

Coverage
--------
- Sepsis        (Surviving Sepsis Campaign 2021 / 2024 updates)
- AKI           (KDIGO 2012 / NICE 2019)
- Shock         (general haemodynamic management)
- Oxygen Therapy (BTS / WHO 2016 / COVID-era evidence)

Each document is intentionally chunked at guideline-section granularity so that
keyword search returns targeted, citable evidence rather than wall-of-text dumps.
"""

from app.rag.document import ClinicalDocument

# ---------------------------------------------------------------------------
# SEPSIS DOCUMENTS
# ---------------------------------------------------------------------------

_SEPSIS_DOCS = [
    ClinicalDocument(
        id="sepsis-definition-2016",
        title="Sepsis-3 Definition and Diagnostic Criteria",
        source="JAMA / Singer et al. 2016",
        category="Sepsis",
        section="Definition",
        content=(
            "Sepsis is defined as life-threatening organ dysfunction caused by a dysregulated host "
            "response to infection (Sepsis-3, 2016). Organ dysfunction is identified by an acute "
            "change in total SOFA score ≥2 points. Septic shock is a subset of sepsis in which "
            "underlying circulatory and cellular/metabolic abnormalities are profound enough to "
            "substantially increase mortality. Patients with septic shock can be identified by a "
            "vasopressor requirement to maintain MAP ≥65 mmHg AND a serum lactate >2 mmol/L in "
            "the absence of hypovolaemia."
        ),
        tags=["sepsis", "septic shock", "sofa", "organ dysfunction", "lactate", "MAP", "definition"],
    ),
    ClinicalDocument(
        id="sepsis-ssc-2021-bundle-1h",
        title="Surviving Sepsis Campaign: 1-Hour Bundle",
        source="Surviving Sepsis Campaign 2021",
        category="Sepsis",
        section="Early Management Bundle",
        content=(
            "The SSC 1-hour bundle (2021) recommends: "
            "(1) Measure lactate; re-measure if initial lactate >2 mmol/L. "
            "(2) Obtain blood cultures before administering antibiotics. "
            "(3) Administer broad-spectrum antibiotics within 1 hour. "
            "(4) Begin rapid administration of 30 mL/kg crystalloid for hypotension or lactate ≥4 mmol/L. "
            "(5) Apply vasopressors if patient is hypotensive during or after fluid resuscitation to maintain MAP ≥65 mmHg. "
            "Norepinephrine is the first-line vasopressor. Evidence grade: Strong recommendation, moderate quality."
        ),
        tags=["sepsis", "1-hour bundle", "antibiotics", "vasopressor", "norepinephrine", "lactate", "fluid", "MAP"],
    ),
    ClinicalDocument(
        id="sepsis-ssc-2021-antibiotics",
        title="Surviving Sepsis Campaign: Antibiotic Therapy",
        source="Surviving Sepsis Campaign 2021",
        category="Sepsis",
        section="Antibiotic Therapy",
        content=(
            "For adults with sepsis or septic shock, the SSC recommends administering antimicrobials "
            "immediately, ideally within 1 hour of recognition. Empiric broad-spectrum therapy covering "
            "likely pathogens is recommended. De-escalation should occur as soon as the pathogen and "
            "sensitivities are identified. Typical empiric choices include piperacillin-tazobactam or "
            "meropenem for Gram-negative coverage, with vancomycin added when MRSA is suspected. "
            "Duration should be guided by clinical improvement and procalcitonin trends."
        ),
        tags=["sepsis", "antibiotics", "meropenem", "piperacillin", "vancomycin", "de-escalation", "procalcitonin"],
    ),
    ClinicalDocument(
        id="sepsis-ssc-2021-vasopressors",
        title="Surviving Sepsis Campaign: Vasopressor Therapy",
        source="Surviving Sepsis Campaign 2021",
        category="Sepsis",
        section="Haemodynamic Support",
        content=(
            "Norepinephrine (noradrenaline) is recommended as the first-line vasopressor in septic shock "
            "(strong recommendation, moderate quality evidence). Target MAP ≥65 mmHg. If norepinephrine "
            "alone is insufficient, vasopressin (up to 0.03 U/min) may be added to raise MAP or reduce "
            "the norepinephrine dose. Epinephrine may be added as a second agent. Dopamine is not "
            "recommended as a vasopressor in septic shock. Corticosteroids (hydrocortisone 200 mg/day) "
            "should be considered if adequate fluids and vasopressors cannot restore haemodynamic stability."
        ),
        tags=["sepsis", "vasopressor", "norepinephrine", "vasopressin", "MAP", "haemodynamic", "shock", "hydrocortisone"],
    ),
    ClinicalDocument(
        id="sepsis-lactate-monitoring",
        title="Lactate Monitoring in Sepsis",
        source="Surviving Sepsis Campaign 2021 / NEJM Evidence",
        category="Sepsis",
        section="Monitoring",
        content=(
            "Serum lactate is a key biomarker for tissue hypoperfusion in sepsis. A lactate >2 mmol/L "
            "suggests tissue hypoperfusion even in normotensive patients (cryptic shock). A lactate "
            "≥4 mmol/L is associated with high mortality and mandates aggressive resuscitation. "
            "Lactate-guided resuscitation (target lactate clearance ≥10% within 2 hours) has been shown "
            "to reduce 28-day mortality compared with MAP-guided resuscitation alone. Serial lactate "
            "measurements every 2–4 hours are recommended until lactate normalises (<2 mmol/L)."
        ),
        tags=["lactate", "sepsis", "tissue hypoperfusion", "cryptic shock", "clearance", "mortality", "monitoring"],
    ),
]

# ---------------------------------------------------------------------------
# AKI DOCUMENTS
# ---------------------------------------------------------------------------

_AKI_DOCS = [
    ClinicalDocument(
        id="aki-kdigo-2012-staging",
        title="KDIGO AKI Staging Criteria",
        source="KDIGO 2012 Clinical Practice Guideline for AKI",
        category="AKI",
        section="Staging",
        content=(
            "AKI is defined and staged by KDIGO 2012 as follows: "
            "Stage 1 – Creatinine rise ≥0.3 mg/dL within 48 h, OR ≥1.5–1.9× baseline within 7 days, "
            "OR urine output <0.5 mL/kg/h for 6–12 h. "
            "Stage 2 – Creatinine 2.0–2.9× baseline, OR urine output <0.5 mL/kg/h for ≥12 h. "
            "Stage 3 – Creatinine ≥3× baseline, OR rise ≥4.0 mg/dL, OR initiation of RRT, "
            "OR urine output <0.3 mL/kg/h for ≥24 h, OR anuria ≥12 h. "
            "Higher staging is associated with increased in-hospital mortality and CKD progression."
        ),
        tags=["AKI", "creatinine", "urine output", "staging", "KDIGO", "kidney", "RRT"],
    ),
    ClinicalDocument(
        id="aki-management-icu",
        title="AKI Management in the ICU",
        source="KDIGO 2012 / NICE CG169 2019",
        category="AKI",
        section="Management",
        content=(
            "Management of AKI in the ICU centres on: "
            "(1) Identification and treatment of the underlying cause (sepsis, nephrotoxins, hypovolaemia). "
            "(2) Optimise renal perfusion — target MAP ≥65 mmHg (≥75 in CKD), avoid hypovolaemia. "
            "(3) Remove nephrotoxic agents: NSAIDs, aminoglycosides, contrast media, ACEi/ARBs when AKI is present. "
            "(4) Monitor fluid balance closely; avoid fluid overload (associated with worse outcomes). "
            "(5) Consider renal replacement therapy (RRT) for AKI Stage 3 with refractory hyperkalemia (K+ >6.5 mEq/L), "
            "metabolic acidosis (pH <7.15), fluid overload, or uraemic complications. "
            "Diuretics may be used for volume overload but do not prevent or treat AKI."
        ),
        tags=["AKI", "ICU", "management", "nephrotoxins", "RRT", "fluid", "MAP", "diuretics", "hyperkalemia"],
    ),
    ClinicalDocument(
        id="aki-creatinine-bun-interpretation",
        title="Creatinine and BUN Interpretation in AKI",
        source="UpToDate / Harrison's Internal Medicine",
        category="AKI",
        section="Biomarkers",
        content=(
            "Serum creatinine is the primary biomarker for detecting and staging AKI. Normal range: "
            "0.6–1.2 mg/dL. In critically ill patients, creatinine may underestimate true GFR loss due "
            "to reduced muscle mass. Blood Urea Nitrogen (BUN) normal range is 7–20 mg/dL. "
            "Elevated BUN with elevated creatinine suggests intrinsic renal injury. "
            "A BUN:creatinine ratio >20 suggests pre-renal aetiology (dehydration, reduced renal perfusion). "
            "A ratio <10 suggests intrinsic renal disease or excess protein catabolism."
        ),
        tags=["creatinine", "BUN", "AKI", "GFR", "renal", "biomarker", "pre-renal"],
    ),
]

# ---------------------------------------------------------------------------
# SHOCK MANAGEMENT DOCUMENTS
# ---------------------------------------------------------------------------

_SHOCK_DOCS = [
    ClinicalDocument(
        id="shock-classification",
        title="Classification of Shock",
        source="European Society of Intensive Care Medicine (ESICM)",
        category="Shock",
        section="Classification",
        content=(
            "Shock is classified into four types based on aetiology: "
            "(1) Distributive shock — septic (most common in ICU), anaphylactic, neurogenic. "
            "Characterised by vasodilation, low SVR, high CO. "
            "(2) Hypovolaemic shock — haemorrhage, burns, GI losses. "
            "Low preload, low CO, high SVR. "
            "(3) Cardiogenic shock — MI, heart failure, arrhythmia. "
            "Low CO, high SVR, high filling pressures. "
            "(4) Obstructive shock — PE, cardiac tamponade, tension pneumothorax. "
            "Mechanical obstruction to flow, low CO. "
            "Bedside assessment: MAP, HR, urine output, lactate, CVP, and echocardiography guide classification."
        ),
        tags=["shock", "distributive", "hypovolaemic", "cardiogenic", "obstructive", "SVR", "cardiac output", "classification"],
    ),
    ClinicalDocument(
        id="shock-fluid-resuscitation",
        title="Fluid Resuscitation in Shock",
        source="Surviving Sepsis Campaign 2021 / SMART Trial 2018",
        category="Shock",
        section="Fluid Therapy",
        content=(
            "Balanced crystalloids (Lactated Ringer's or PlasmaLyte) are preferred over normal saline "
            "for resuscitation in the ICU based on the SMART trial (2018), which showed lower incidence "
            "of major adverse kidney events with balanced solutions. Normal saline (0.9% NaCl) causes "
            "hyperchloraemic metabolic acidosis when given in large volumes. "
            "Initial resuscitation: 30 mL/kg IV crystalloid within 3 hours for septic shock. "
            "Beyond the initial bolus, fluid responsiveness should guide further fluid therapy — "
            "dynamic measures (pulse pressure variation, stroke volume variation, passive leg raise) "
            "are preferred over static measures (CVP). Avoid fluid overload (positive fluid balance "
            "is associated with worse outcomes)."
        ),
        tags=["shock", "fluid", "crystalloid", "normal saline", "lactated ringer", "balanced", "resuscitation", "fluid overload"],
    ),
    ClinicalDocument(
        id="shock-haemodynamic-monitoring",
        title="Haemodynamic Monitoring in Shock",
        source="ESICM / PAC-Man / ProCESS Trials",
        category="Shock",
        section="Monitoring",
        content=(
            "Haemodynamic monitoring targets in shock: "
            "MAP ≥65 mmHg (higher target ≥75 mmHg for patients with chronic hypertension or AKI). "
            "Heart rate: target 60–100 bpm; tachycardia indicates persistent hypovolaemia or catecholamine excess. "
            "Urine output: target ≥0.5 mL/kg/h as a surrogate of organ perfusion. "
            "ScvO2 ≥70% or SvO2 ≥65% indicate adequate oxygen delivery. "
            "Lactate clearance ≥10% per 2 hours is a therapeutic target. "
            "Arterial line monitoring is recommended for continuous MAP and arterial blood gas analysis. "
            "PA catheters are not routinely recommended but may guide management in complex cardiogenic shock."
        ),
        tags=["shock", "MAP", "haemodynamic", "monitoring", "heart rate", "urine output", "lactate", "ScvO2", "arterial line"],
    ),
]

# ---------------------------------------------------------------------------
# OXYGEN THERAPY DOCUMENTS
# ---------------------------------------------------------------------------

_OXYGEN_DOCS = [
    ClinicalDocument(
        id="oxygen-targets-icu",
        title="Oxygen Therapy Targets in the ICU",
        source="BTS Guideline 2017 / ICU-ROX Trial 2019",
        category="Oxygen Therapy",
        section="Targets",
        content=(
            "The British Thoracic Society (BTS) 2017 guideline recommends: "
            "Target SpO2 94–98% for most acutely ill patients. "
            "Target SpO2 88–92% for patients at risk of hypercapnic respiratory failure (COPD, obesity hypoventilation). "
            "Hypoxaemia (SpO2 <88%) requires urgent supplemental oxygen. "
            "Hyperoxia should be avoided — the ICU-ROX trial (2019) found that conservative oxygen therapy "
            "(targeting SpO2 91–96%) was non-inferior to liberal oxygen therapy and may reduce mortality "
            "in mechanically ventilated ICU patients. A SpO2 >96% with FiO2 >0.5 warrants weaning of oxygen."
        ),
        tags=["oxygen", "SpO2", "target", "hyperoxia", "hypoxia", "BTS", "ICU", "COPD", "mechanical ventilation"],
    ),
    ClinicalDocument(
        id="oxygen-delivery-devices",
        title="Oxygen Delivery Devices and Flow Rates",
        source="BTS Guideline 2017",
        category="Oxygen Therapy",
        section="Delivery Devices",
        content=(
            "Oxygen delivery devices and approximate FiO2: "
            "Nasal cannula (1–6 L/min): FiO2 0.24–0.44. Suitable for mild hypoxia. "
            "Simple face mask (5–10 L/min): FiO2 0.35–0.50. "
            "Non-rebreather mask (10–15 L/min): FiO2 0.60–0.80. Use for severe acute hypoxia. "
            "Venturi mask: Delivers precise FiO2 (24–60%) — preferred when accurate FiO2 is critical (e.g. COPD). "
            "High-Flow Nasal Oxygen (HFNO, 30–60 L/min): FiO2 up to 1.0, provides modest PEEP effect. "
            "Indicated for moderate-severe hypoxic respiratory failure. "
            "Non-invasive ventilation (NIV/CPAP/BiPAP): For type 2 respiratory failure or cardiogenic pulmonary oedema."
        ),
        tags=["oxygen", "nasal cannula", "face mask", "non-rebreather", "venturi", "HFNO", "NIV", "FiO2", "delivery"],
    ),
    ClinicalDocument(
        id="oxygen-spo2-interpretation",
        title="SpO2 Interpretation and Clinical Significance",
        source="WHO Pulse Oximetry Training Manual / BTS 2017",
        category="Oxygen Therapy",
        section="Monitoring",
        content=(
            "SpO2 (peripheral oxygen saturation) measured by pulse oximetry reflects haemoglobin oxygen "
            "saturation. Normal: 94–100%. "
            "SpO2 88–93%: Mild-moderate hypoxia. Supplemental oxygen indicated. Investigate cause. "
            "SpO2 85–88%: Moderate hypoxia. Increase FiO2, consider HFNO or NIV. "
            "SpO2 <85%: Severe hypoxia. Urgent intervention required. Consider intubation. "
            "Limitations: SpO2 is unreliable in poor perfusion states, carbon monoxide poisoning "
            "(SpO2 reads falsely normal), severe anaemia, or dark skin pigmentation. "
            "Arterial blood gas (ABG) for PaO2 is the gold standard for hypoxia assessment."
        ),
        tags=["SpO2", "oxygen", "hypoxia", "pulse oximetry", "ABG", "PaO2", "saturation", "interpretation"],
    ),
]

# ---------------------------------------------------------------------------
# Aggregated corpus
# ---------------------------------------------------------------------------

from app.rag.surviving_sepsis import DOCUMENTS as ssc_docs
from app.rag.kdigo import DOCUMENTS as kdigo_docs
from app.rag.who import DOCUMENTS as who_docs
from app.rag.nice import DOCUMENTS as nice_docs
from app.rag.drugs import DRUG_DOCUMENTS as drug_docs

ALL_CLINICAL_DOCUMENTS: list[ClinicalDocument] = (
    _SEPSIS_DOCS + _AKI_DOCS + _SHOCK_DOCS + _OXYGEN_DOCS +
    ssc_docs + kdigo_docs + who_docs + nice_docs + drug_docs
)
