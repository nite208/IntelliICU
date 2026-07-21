"""
app/rag/who.py

World Health Organization (WHO) clinical guidelines for oxygen therapy, sepsis, and critical care.
"""

from app.rag.document import ClinicalDocument

DOCUMENTS = [
    ClinicalDocument(
        id="who-oxygen-hypoxemia-2016",
        title="WHO 2016: Oxygen Therapy for Severe Acute Respiratory Infection",
        source="World Health Organization 2016",
        category="Oxygen Therapy",
        section="Oxygen Administration",
        content=(
            "Initiate oxygen therapy immediately in patients with emergency signs (obstructed breathing, "
            "severe respiratory distress, central cyanosis, or shock) or SpO2 <90% (<94% in pregnant patients). "
            "Deliver oxygen to maintain target SpO2 ≥90% in non-pregnant adults and ≥92-95% in pregnant "
            "patients. Use a flow rate of at least 5 L/min with nasal cannula or simple face mask, or "
            "10-15 L/min with a reservoir mask in severe distress."
        ),
        tags=["oxygen", "WHO", "hypoxemia", "respiratory", "SpO2", "pregnancy"],
    ),
    ClinicalDocument(
        id="who-sepsis-screening-2020",
        title="WHO 2020: Sepsis Prevention and Early Identification",
        source="World Health Organization Sepsis Report 2020",
        category="Sepsis",
        section="Identification",
        content=(
            "Early identification of sepsis requires active screening using simple clinical criteria such "
            "as the Quick Sequential Organ Failure Assessment (qSOFA) or National Early Warning Score (NEWS2) "
            "in low- and middle-income countries. Key signs include altered mental status, systolic blood "
            "pressure ≤100 mmHg, and respiratory rate ≥22 breaths per minute. Sepsis prevention centers on "
            "infection prevention and control (IPC) and hand hygiene."
        ),
        tags=["sepsis", "screening", "qSOFA", "NEWS2", "identification", "prevention", "hygiene"],
    ),
    ClinicalDocument(
        id="who-airway-management-2021",
        title="WHO 2021: Airway and Ventilatory Support in COVID-19",
        source="World Health Organization COVID-19 Guidelines 2021",
        category="Oxygen Therapy",
        section="Ventilatory Support",
        content=(
            "In patients with COVID-19 and acute hypoxemic respiratory failure, high-flow nasal oxygen (HFNO) "
            "or non-invasive ventilation (NIV) should be preferred over standard oxygen therapy if available, "
            "provided the patient has no urgent indication for endotracheal intubation. Close monitoring "
            "for clinical deterioration is essential, as delayed intubation is associated with poor outcomes."
        ),
        tags=["oxygen", "airway", "HFNO", "NIV", "intubation", "ventilation", "COVID-19"],
    ),
]
