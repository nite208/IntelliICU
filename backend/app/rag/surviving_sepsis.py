"""
app/rag/surviving_sepsis.py

Surviving Sepsis Campaign (SSC) 2021/2024 detailed clinical guidelines.
"""

from app.rag.document import ClinicalDocument

DOCUMENTS = [
    ClinicalDocument(
        id="ssc-fluid-resuscitation-2021",
        title="SSC 2021: Fluid Resuscitation Volume and Type",
        source="Surviving Sepsis Campaign 2021",
        category="Sepsis",
        section="Resuscitation",
        content=(
            "For adults with sepsis or septic shock, we recommend administering at least 30 mL/kg "
            "of intravenous crystalloid fluid within the first 3 hours of presentation. We suggest "
            "using balanced crystalloids (e.g., Lactated Ringer's or Plasma-Lyte) instead of normal "
            "saline (0.9% NaCl) for resuscitation. For patients requiring substantial volumes of "
            "crystalloids, we suggest using albumin in addition to crystalloids over crystalloids alone."
        ),
        tags=["sepsis", "resuscitation", "crystalloids", "balanced", "saline", "albumin", "fluid"],
    ),
    ClinicalDocument(
        id="ssc-antimicrobial-timing-2021",
        title="SSC 2021: Antimicrobial Timing and Administration",
        source="Surviving Sepsis Campaign 2021",
        category="Sepsis",
        section="Antimicrobial Therapy",
        content=(
            "For adults with suspected septic shock or a high likelihood of sepsis, we recommend "
            "administering antimicrobials immediately, ideally within 1 hour of recognition. For "
            "adults with possible sepsis without shock, we suggest a time-limited course of rapid "
            "investigation, and if concern for infection persists, administer antimicrobials within "
            "3 hours of first recognition."
        ),
        tags=["sepsis", "antibiotics", "antimicrobials", "timing", "1-hour bundle", "infection"],
    ),
    ClinicalDocument(
        id="ssc-vasopressors-targets-2021",
        title="SSC 2021: Vasoactive Targets and Choices",
        source="Surviving Sepsis Campaign 2021",
        category="Sepsis",
        section="Hemodynamic Support",
        content=(
            "For adults with septic shock, we recommend norepinephrine as the first-line vasopressor "
            "over other agents. We suggest targeting a mean arterial pressure (MAP) of 65 mmHg. "
            "For patients with septic shock on norepinephrine with inadequate MAP, we suggest adding "
            "vasopressin as a second-line agent (usually at a fixed rate of 0.03 units/min) instead of "
            "escalating norepinephrine dose."
        ),
        tags=["sepsis", "vasopressors", "norepinephrine", "vasopressin", "MAP", "shock"],
    ),
    ClinicalDocument(
        id="ssc-steroids-adjunctive-2021",
        title="SSC 2021: Corticosteroids in Septic Shock",
        source="Surviving Sepsis Campaign 2021",
        category="Sepsis",
        section="Adjunctive Therapy",
        content=(
            "For adults with septic shock and an ongoing requirement for vasopressor therapy "
            "(typically defined as norepinephrine or equivalent dose ≥0.25 mcg/kg/min for at least "
            "4 hours), we suggest using intravenous corticosteroids. The recommended regimen is "
            "intravenous hydrocortisone at a dose of 200 mg/day (administered as 50 mg IV every 6 hours "
            "or as a continuous infusion)."
        ),
        tags=["sepsis", "steroids", "hydrocortisone", "vasopressor", "septic shock", "corticosteroids"],
    ),
]
