"""
Clinical Guideline Retriever.
Acts as the knowledge base for clinical practice guidelines (Surviving Sepsis, WHO, NIH, PubMed).
"""

from typing import Dict, Any, List

class GuidelineRetriever:
    """
    Local knowledge base holding evidence-based clinical practice guidelines.
    """

    def __init__(self):
        self.kb = [
            {
                "topic": "norepinephrine",
                "keywords": ["norepinephrine", "vasopressor", "pressor", "levophed"],
                "answer": "Norepinephrine is recommended as the first-choice vasopressor for adults with septic shock to maintain a Mean Arterial Pressure (MAP) target of >= 65 mmHg, acting primarily via alpha-1 adrenergic receptors to increase systemic vascular resistance.",
                "evidence": [
                    "Strongly preferred over dopamine due to a lower risk of arrhythmic events and decreased mortality rates in fluid-refractory shock.",
                    "Adjunctive vasopressin (up to 0.03 units/min) may be added to reduce norepinephrine dose requirements.",
                    "Sparsely triggers beta-1 activity compared to epinephrine, minimizing secondary myocardial oxygen demand."
                ],
                "guideline": "International Guidelines for Management of Sepsis and Septic Shock",
                "source": "Surviving Sepsis Campaign 2024",
                "publication_year": 2024,
                "confidence": 0.98
            },
            {
                "topic": "sepsis_management",
                "keywords": ["sepsis management", "sepsis protocol", "sepsis bundle", "sepsis treatment", "explain sepsis"],
                "answer": "Sepsis management centers on the Surviving Sepsis 1-hour and 3-hour bundle guidelines: measure lactate levels, obtain blood cultures before administering broad-spectrum antibiotics, and administer 30 mL/kg of crystalloid fluid for hypotension or lactate >= 4.0 mmol/L.",
                "evidence": [
                    "Compliance with the Surviving Sepsis bundles is associated with a 15-20% relative reduction in hospital mortality.",
                    "Broad-spectrum IV antibiotics should be initiated within 1 hour of recognition of septic shock or high probability of sepsis.",
                    "Dynamic measures of fluid responsiveness (passive leg raise, stroke volume variation) are preferred over static pressure targets."
                ],
                "guideline": "WHO Guidelines on Sepsis Prevention and Management",
                "source": "World Health Organization (WHO) Consensus",
                "publication_year": 2023,
                "confidence": 0.96
            },
            {
                "topic": "lactate",
                "keywords": ["monitor lactate", "lactate importance", "why lactate", "lactate clearance", "lactate level"],
                "answer": "Serial lactate monitoring is recommended to assess tissue perfusion and guide resuscitation therapy in sepsis. A lactate level > 2.0 mmol/L suggests tissue hypoperfusion, anaerobic glycolysis, or impaired hepatic clearance.",
                "evidence": [
                    "Lactate-guided resuscitation (targeting a 10% clearance every 2 hours) yields significant relative reductions in mortality compared to standard care.",
                    "Persistent hyperlactatemia (>4.0 mmol/L) is a strong independent predictor of multi-organ failure and intensive care mortality.",
                    "Elevations may also occur due to beta-2 adrenergic stimulation from endogenous or exogenous epinephrine."
                ],
                "guideline": "Clinical Utility of Serial Lactate in Severe Sepsis Meta-Analysis",
                "source": "PubMed / National Institutes of Health (NIH)",
                "publication_year": 2022,
                "confidence": 0.94
            },
            {
                "topic": "map",
                "keywords": ["map important", "mean arterial pressure", "why map", "target map", "perfusion pressure"],
                "answer": "Mean Arterial Pressure (MAP) represents the average perfusion pressure in the systemic circulation. Targeting a MAP of >= 65 mmHg is recommended to maintain essential perfusion to vital organs (brain, kidneys, heart).",
                "evidence": [
                    "MAP levels below 60-65 mmHg are associated with immediate tissue hypoperfusion and acute kidney injury (AKI).",
                    "Targeting higher MAP values (e.g., 85 mmHg) does not reduce mortality or organ failure rates except in patients with chronic hypertension.",
                    "Diastolic arterial pressure (DAP) < 40 mmHg suggests severe arterial vasodilation and should prompt immediate vasopressor support."
                ],
                "guideline": "Hemodynamic Monitoring Guidelines in Critical Care",
                "source": "PubMed / NIH Consensus Panel",
                "publication_year": 2024,
                "confidence": 0.97
            }
        ]

    def retrieve(self, question: str) -> Dict[str, Any] | None:
        """
        Scans keywords against the user query. Returns the first matching guideline structure or None.
        """
        q_lower = question.lower()
        for doc in self.kb:
            for kw in doc["keywords"]:
                if kw in q_lower:
                    return {
                        "answer": doc["answer"],
                        "evidence": doc["evidence"],
                        "guideline": doc["guideline"],
                        "source": doc["source"],
                        "publication_year": doc["publication_year"],
                        "confidence": doc["confidence"]
                    }
        return None
