"""
app/rag/drugs.py

Medication knowledge base for critical care drugs in the ICU.
Includes vasoactives, inotropes, broad-spectrum antibiotics, and diuretics.
"""

from app.rag.document import ClinicalDocument

# Helper function to generate content string from fields to ensure indexing
def _build_content(
    generic_name: str,
    drug_class: str,
    indications: str,
    contraindications: str,
    mechanism: str,
    dosing: str,
    renal_adjustment: str,
    monitoring: str,
    adverse_effects: str,
    interactions: str
) -> str:
    return (
        f"Generic Name: {generic_name}\n"
        f"Class: {drug_class}\n"
        f"Indications: {indications}\n"
        f"Contraindications: {contraindications}\n"
        f"Mechanism: {mechanism}\n"
        f"Dosing: {dosing}\n"
        f"Renal Adjustment: {renal_adjustment}\n"
        f"Monitoring: {monitoring}\n"
        f"Adverse Effects: {adverse_effects}\n"
        f"Interactions: {interactions}"
    )

DRUG_DOCUMENTS = [
    ClinicalDocument(
        id="drug-norepinephrine",
        title="Norepinephrine Clinical Profile",
        source="FDA / Surviving Sepsis Campaign 2021",
        category="Drug",
        section="Clinical Profile",
        generic_name="Norepinephrine",
        drug_class="Vasopressor; Alpha-1 & Beta-1 Adrenergic Agonist",
        indications="First-line vasopressor for septic shock, distributive shock, cardiogenic shock, and severe hypotension refractory to fluid resuscitation.",
        contraindications="Hypovolemia (unless emergency resuscitation is underway), mesenteric vascular thrombosis, severe hypoxia or hypercapnia.",
        mechanism="Acts primarily on alpha-1 adrenergic receptors to cause vasoconstriction (increasing SVR and MAP). Spares beta-1 adrenergic receptors slightly to provide modest positive inotropic effects with less tachycardia than epinephrine.",
        dosing="Continuous IV infusion via central venous line. Start at 0.05-0.1 mcg/kg/min; titrate to maintain target MAP (typically >= 65 mmHg). Max dose is usually 1-2 mcg/kg/min depending on clinical protocol.",
        renal_adjustment="No renal dosage adjustment required. Monitor urine output closely as excessive vasoconstriction can impair renal perfusion.",
        monitoring="Continuous arterial line blood pressure, heart rate, EKG, urine output, lactate clearance, infusion site integrity (monitor for extravasation).",
        adverse_effects="Arrhythmias (tachycardia, atrial fibrillation), myocardial ischemia, peripheral tissue ischemia/gangrene (especially with extravasation or prolonged high doses), anxiety, skin necrosis.",
        interactions="Beta-blockers (antagonize cardiac effects), MAO inhibitors and tricyclic antidepressants (potentiate vasopressor response), halogenated anesthetics (increase risk of ventricular arrhythmias).",
        tags=["norepinephrine", "noradrenaline", "vasopressor", "sepsis", "shock", "MAP", "constriction", "levophed"],
        content=_build_content(
            generic_name="Norepinephrine",
            drug_class="Vasopressor; Alpha-1 & Beta-1 Adrenergic Agonist",
            indications="First-line vasopressor for septic shock, distributive shock, cardiogenic shock, and severe hypotension refractory to fluid resuscitation.",
            contraindications="Hypovolemia (unless emergency resuscitation is underway), mesenteric vascular thrombosis, severe hypoxia or hypercapnia.",
            mechanism="Acts primarily on alpha-1 adrenergic receptors to cause vasoconstriction (increasing SVR and MAP). Spares beta-1 adrenergic receptors slightly to provide modest positive inotropic effects with less tachycardia than epinephrine.",
            dosing="Continuous IV infusion via central venous line. Start at 0.05-0.1 mcg/kg/min; titrate to maintain target MAP (typically >= 65 mmHg). Max dose is usually 1-2 mcg/kg/min depending on clinical protocol.",
            renal_adjustment="No renal dosage adjustment required. Monitor urine output closely as excessive vasoconstriction can impair renal perfusion.",
            monitoring="Continuous arterial line blood pressure, heart rate, EKG, urine output, lactate clearance, infusion site integrity (monitor for extravasation).",
            adverse_effects="Arrhythmias (tachycardia, atrial fibrillation), myocardial ischemia, peripheral tissue ischemia/gangrene (especially with extravasation or prolonged high doses), anxiety, skin necrosis.",
            interactions="Beta-blockers (antagonize cardiac effects), MAO inhibitors and tricyclic antidepressants (potentiate vasopressor response), halogenated anesthetics (increase risk of ventricular arrhythmias)."
        )
    ),
    ClinicalDocument(
        id="drug-vasopressin",
        title="Vasopressin Clinical Profile",
        source="FDA / Surviving Sepsis Campaign 2021",
        category="Drug",
        section="Clinical Profile",
        generic_name="Vasopressin",
        drug_class="Vasopressor; Antidiuretic Hormone (ADH) Analog",
        indications="Second-line/adjunct vasopressor in septic shock or distributive shock to reduce norepinephrine requirements and raise MAP. Also used in diabetes insipidus.",
        contraindications="Hypersensitivity to vasopressin, bilateral chronic renal failure with anuria.",
        mechanism="Stimulates V1 receptors on vascular smooth muscle to cause direct peripheral vasoconstriction. Stimulates V2 receptors in renal collecting ducts to increase water reabsorption.",
        dosing="Continuous IV infusion via central line. Administered at a fixed rate of 0.03-0.04 units/min. Do not titrate for septic shock resuscitation to avoid excessive coronary and splanchnic vasoconstriction.",
        renal_adjustment="No renal dose adjustment required for shock management. Monitor urine output and fluid balance due to V2-mediated water retention.",
        monitoring="Arterial blood pressure, heart rate, fluid balance, serum sodium, urine output, peripheral perfusion.",
        adverse_effects="Hyponatremia (water retention), myocardial ischemia, mesenteric ischemia, digital ischemia, bradycardia, cardiac output reduction.",
        interactions="Indomethacin (may potentiate antidiuretic effect), ganglionic blocking agents (may increase vasopressor response).",
        tags=["vasopressin", "ADH", "pitressin", "septic shock", "V1 receptor", "V2 receptor", "hyponatremia", "adjunct"],
        content=_build_content(
            generic_name="Vasopressin",
            drug_class="Vasopressor; Antidiuretic Hormone (ADH) Analog",
            indications="Second-line/adjunct vasopressor in septic shock or distributive shock to reduce norepinephrine requirements and raise MAP. Also used in diabetes insipidus.",
            contraindications="Hypersensitivity to vasopressin, bilateral chronic renal failure with anuria.",
            mechanism="Stimulates V1 receptors on vascular smooth muscle to cause direct peripheral vasoconstriction. Stimulates V2 receptors in renal collecting ducts to increase water reabsorption.",
            dosing="Continuous IV infusion via central line. Administered at a fixed rate of 0.03-0.04 units/min. Do not titrate for septic shock resuscitation to avoid excessive coronary and splanchnic vasoconstriction.",
            renal_adjustment="No renal dose adjustment required for shock management. Monitor urine output and fluid balance due to V2-mediated water retention.",
            monitoring="Arterial blood pressure, heart rate, fluid balance, serum sodium, urine output, peripheral perfusion.",
            adverse_effects="Hyponatremia (water retention), myocardial ischemia, mesenteric ischemia, digital ischemia, bradycardia, cardiac output reduction.",
            interactions="Indomethacin (may potentiate antidiuretic effect), ganglionic blocking agents (may increase vasopressor response)."
        )
    ),
    ClinicalDocument(
        id="drug-epinephrine",
        title="Epinephrine Clinical Profile",
        source="FDA / American Heart Association",
        category="Drug",
        section="Clinical Profile",
        generic_name="Epinephrine",
        drug_class="Vasopressor; Inotrope; Alpha & Beta Adrenergic Agonist",
        indications="Anaphylaxis, cardiac arrest (asystole, PEA, VF/pVT), severe cardiogenic shock, or as a third-line vasopressor in refractory septic shock.",
        contraindications="None in life-threatening emergency situations. Relative: severe coronary artery disease, narrow-angle glaucoma.",
        mechanism="Agonizes alpha-1 receptors (causing vasoconstriction), beta-1 receptors (increasing heart rate, contractility, and cardiac output), and beta-2 receptors (bronchodilation).",
        dosing="Anaphylaxis: 0.3 mg IM. Cardiac Arrest: 1 mg IV push every 3-5 min. Continuous IV infusion: 0.05-0.5 mcg/kg/min titrated to hemodynamic target.",
        renal_adjustment="No renal dosage adjustment required. Monitor renal perfusion due to potent renal vasoconstriction at higher infusion rates.",
        monitoring="Continuous arterial line, EKG (risk of ventricular arrhythmias), serum lactate (epinephrine induces aerobic glycolysis, leading to transient benign lactate rises).",
        adverse_effects="Tachyarrhythmias, ventricular fibrillation, lactic acidosis (transient), myocardial ischemia, pulmonary edema, severe hypertension.",
        interactions="Beta-blockers (severe hypertension and bradycation), halogenated anesthetics (arrhythmias), cocaine or tricyclic antidepressants (enhanced cardiovascular effects).",
        tags=["epinephrine", "adrenaline", "anaphylaxis", "cardiac arrest", "arrhythmia", "inotrope", "beta agonist"],
        content=_build_content(
            generic_name="Epinephrine",
            drug_class="Vasopressor; Inotrope; Alpha & Beta Adrenergic Agonist",
            indications="Anaphylaxis, cardiac arrest (asystole, PEA, VF/pVT), severe cardiogenic shock, or as a third-line vasopressor in refractory septic shock.",
            contraindications="None in life-threatening emergency situations. Relative: severe coronary artery disease, narrow-angle glaucoma.",
            mechanism="Agonizes alpha-1 receptors (causing vasoconstriction), beta-1 receptors (increasing heart rate, contractility, and cardiac output), and beta-2 receptors (bronchodilation).",
            dosing="Anaphylaxis: 0.3 mg IM. Cardiac Arrest: 1 mg IV push every 3-5 min. Continuous IV infusion: 0.05-0.5 mcg/kg/min titrated to hemodynamic target.",
            renal_adjustment="No renal dosage adjustment required. Monitor renal perfusion due to potent renal vasoconstriction at higher infusion rates.",
            monitoring="Continuous arterial line, EKG (risk of ventricular arrhythmias), serum lactate (epinephrine induces aerobic glycolysis, leading to transient benign lactate rises).",
            adverse_effects="Tachyarrhythmias, ventricular fibrillation, lactic acidosis (transient), myocardial ischemia, pulmonary edema, severe hypertension.",
            interactions="Beta-blockers (severe hypertension and bradycation), halogenated anesthetics (arrhythmias), cocaine or tricyclic antidepressants (enhanced cardiovascular effects)."
        )
    ),
    ClinicalDocument(
        id="drug-dobutamine",
        title="Dobutamine Clinical Profile",
        source="FDA / ACC/AHA Heart Failure Guidelines",
        category="Drug",
        section="Clinical Profile",
        generic_name="Dobutamine",
        drug_class="Inotrope; Beta-1 Adrenergic Agonist",
        indications="Short-term management of acute decompensated heart failure, cardiogenic shock, and septic shock with myocardial dysfunction (low cardiac index with adequate MAP).",
        contraindications="Idiopathic hypertrophic subaortic stenosis, severe hypersensitivity.",
        mechanism="Selectively stimulates beta-1 adrenergic receptors to increase myocardial contractility and stroke volume, with minor beta-2 activation (vasodilation) and alpha-1 agonist balance.",
        dosing="Continuous IV infusion via central or peripheral line. 2.5-20 mcg/kg/min titrated to cardiac output/cardiac index goals. Start at 2.5-5 mcg/kg/min.",
        renal_adjustment="No renal dosage adjustment required.",
        monitoring="Heart rate, blood pressure (risk of hypotension due to beta-2 vasodilation), cardiac output/index, EKG, urine output, serum potassium (potential hypokalemia).",
        adverse_effects="Tachycardia, ventricular ectopic activity/arrhythmias, hypotension (vasodilation), headache, anginal pain, palpitations.",
        interactions="Beta-blockers (mutual antagonism), nitroprusside (synergistic increase in cardiac output), halogenated anesthetics (arrhythmia risk).",
        tags=["dobutamine", "inotrope", "beta-1 agonist", "cardiac output", "heart failure", "contractility", "dobutrex"],
        content=_build_content(
            generic_name="Dobutamine",
            drug_class="Inotrope; Beta-1 Adrenergic Agonist",
            indications="Short-term management of acute decompensated heart failure, cardiogenic shock, and septic shock with myocardial dysfunction (low cardiac index with adequate MAP).",
            contraindications="Idiopathic hypertrophic subaortic stenosis, severe hypersensitivity.",
            mechanism="Selectively stimulates beta-1 adrenergic receptors to increase myocardial contractility and stroke volume, with minor beta-2 activation (vasodilation) and alpha-1 agonist balance.",
            dosing="Continuous IV infusion via central or peripheral line. 2.5-20 mcg/kg/min titrated to cardiac output/cardiac index goals. Start at 2.5-5 mcg/kg/min.",
            renal_adjustment="No renal dosage adjustment required.",
            monitoring="Heart rate, blood pressure (risk of hypotension due to beta-2 vasodilation), cardiac output/index, EKG, urine output, serum potassium (potential hypokalemia).",
            adverse_effects="Tachycardia, ventricular ectopic activity/arrhythmias, hypotension (vasodilation), headache, anginal pain, palpitations.",
            interactions="Beta-blockers (mutual antagonism), nitroprusside (synergistic increase in cardiac output), halogenated anesthetics (arrhythmia risk)."
        )
    ),
    ClinicalDocument(
        id="drug-meropenem",
        title="Meropenem Clinical Profile",
        source="FDA / IDSA Guidelines",
        category="Drug",
        section="Clinical Profile",
        generic_name="Meropenem",
        drug_class="Carbapenem Antibiotic; Beta-lactam",
        indications="Empiric or directed therapy for severe intra-abdominal infections, complicated urinary tract infections, nosocomial pneumonia, and meningitis/sepsis with multi-drug resistant Gram-negative bacilli.",
        contraindications="Severe hypersensitivity to carbapenems or anaphylactic reactions to other beta-lactams.",
        mechanism="Inhibits bacterial cell wall synthesis by binding to and inactivating Penicillin-Binding Proteins (PBPs), leading to cell lysis. Highly resistant to beta-lactamases.",
        dosing="Standard dose: 1 g IV every 8 hours. Severe/meningitis infections: 2 g IV every 8 hours. Administered over 30 minutes, or as prolonged/continuous infusion (over 3-4 hours) in critically ill patients.",
        renal_adjustment="Required: CrCl 30-50 mL/min: 1 g every 12 hours; CrCl 10-29 mL/min: 500 mg every 12 hours; CrCl < 10 mL/min: 500 mg every 24 hours.",
        monitoring="Complete blood count, renal function, liver enzymes, neurological status (rare risk of seizures, particularly in renal impairment).",
        adverse_effects="Seizures (rare compared to imipenem), diarrhea, headache, nausea, skin rash, C. difficile-associated diarrhea, hypersensitivity.",
        interactions="Valproic acid (meropenem severely decreases valproate levels, risking loss of seizure control), Probenecid (prolongs meropenem half-life).",
        tags=["meropenem", "carbapenem", "antibiotic", "sepsis", "renal adjustment", "seizures", "valproic acid", "merrem"],
        content=_build_content(
            generic_name="Meropenem",
            drug_class="Carbapenem Antibiotic; Beta-lactam",
            indications="Empiric or directed therapy for severe intra-abdominal infections, complicated urinary tract infections, nosocomial pneumonia, and meningitis/sepsis with multi-drug resistant Gram-negative bacilli.",
            contraindications="Severe hypersensitivity to carbapenems or anaphylactic reactions to other beta-lactams.",
            mechanism="Inhibits bacterial cell wall synthesis by binding to and inactivating Penicillin-Binding Proteins (PBPs), leading to cell lysis. Highly resistant to beta-lactamases.",
            dosing="Standard dose: 1 g IV every 8 hours. Severe/meningitis infections: 2 g IV every 8 hours. Administered over 30 minutes, or as prolonged/continuous infusion (over 3-4 hours) in critically ill patients.",
            renal_adjustment="Required: CrCl 30-50 mL/min: 1 g every 12 hours; CrCl 10-29 mL/min: 500 mg every 12 hours; CrCl < 10 mL/min: 500 mg every 24 hours.",
            monitoring="Complete blood count, renal function, liver enzymes, neurological status (rare risk of seizures, particularly in renal impairment).",
            adverse_effects="Seizures (rare compared to imipenem), diarrhea, headache, nausea, skin rash, C. difficile-associated diarrhea, hypersensitivity.",
            interactions="Valproic acid (meropenem severely decreases valproate levels, risking loss of seizure control), Probenecid (prolongs meropenem half-life)."
        )
    ),
    ClinicalDocument(
        id="drug-piperacillin-tazobactam",
        title="Piperacillin/Tazobactam Clinical Profile",
        source="FDA / IDSA Guidelines",
        category="Drug",
        section="Clinical Profile",
        generic_name="Piperacillin/Tazobactam",
        drug_class="Penicillin Antibiotic & Beta-Lactamase Inhibitor",
        indications="Broad-spectrum treatment for moderate-to-severe infections, including nosocomial pneumonia, intra-abdominal infections, skin/soft tissue infections, and neutropenic fever. Active against Pseudomonas aeruginosa.",
        contraindications="History of allergic reactions to penicillins, cephalosporins, or beta-lactamase inhibitors.",
        mechanism="Piperacillin inhibits cell wall synthesis by binding to PBPs. Tazobactam is a beta-lactamase inhibitor that protects piperacillin from enzymatic degradation by beta-lactamase-producing bacteria.",
        dosing="Standard dose: 4.5 g IV every 6 hours (standard infusion) or 4.5 g IV every 8 hours administered as a prolonged infusion (over 4 hours) to optimize pharmacodynamics.",
        renal_adjustment="Required: CrCl 20-40 mL/min: 3.375 g every 6 hours (or 4.5 g every 8 hours); CrCl < 20 mL/min: 2.25 g every 6 hours (or 3.375 g every 8 hours). Adjust for CRRT.",
        monitoring="Renal function (BUN/creatinine), electrolytes (hypokalemia and hypernatremia risk), CBC (thrombocytopenia risk, neutropenia with prolonged use), signs of bleeding.",
        adverse_effects="Hypersensitivity/anaphylaxis, diarrhea, skin rash (Stevens-Johnson risk), thrombocytopenia, interstitial nephritis, hypokalemia.",
        interactions="Aminoglycosides (physical incompatibility in same IV line), Vecuronium (prolongs neuromuscular blockade), Methotrexate (piperacillin decreases excretion).",
        tags=["piperacillin", "tazobactam", "zosyn", "pseudomonas", "antibiotic", "broad spectrum", "renal adjustment"],
        content=_build_content(
            generic_name="Piperacillin/Tazobactam",
            drug_class="Penicillin Antibiotic & Beta-Lactamase Inhibitor",
            indications="Broad-spectrum treatment for moderate-to-severe infections, including nosocomial pneumonia, intra-abdominal infections, skin/soft tissue infections, and neutropenic fever. Active against Pseudomonas aeruginosa.",
            contraindications="History of allergic reactions to penicillins, cephalosporins, or beta-lactamase inhibitors.",
            mechanism="Piperacillin inhibits cell wall synthesis by binding to PBPs. Tazobactam is a beta-lactamase inhibitor that protects piperacillin from enzymatic degradation by beta-lactamase-producing bacteria.",
            dosing="Standard dose: 4.5 g IV every 6 hours (standard infusion) or 4.5 g IV every 8 hours administered as a prolonged infusion (over 4 hours) to optimize pharmacodynamics.",
            renal_adjustment="Required: CrCl 20-40 mL/min: 3.375 g every 6 hours (or 4.5 g every 8 hours); CrCl < 20 mL/min: 2.25 g every 6 hours (or 3.375 g every 8 hours). Adjust for CRRT.",
            monitoring="Renal function (BUN/creatinine), electrolytes (hypokalemia and hypernatremia risk), CBC (thrombocytopenia risk, neutropenia with prolonged use), signs of bleeding.",
            adverse_effects="Hypersensitivity/anaphylaxis, diarrhea, skin rash (Stevens-Johnson risk), thrombocytopenia, interstitial nephritis, hypokalemia.",
            interactions="Aminoglycosides (physical incompatibility in same IV line), Vecuronium (prolongs neuromuscular blockade), Methotrexate (piperacillin decreases excretion)."
        )
    ),
    ClinicalDocument(
        id="drug-vancomycin",
        title="Vancomycin Clinical Profile",
        source="FDA / ASHP/IDSA 2020 Guidelines",
        category="Drug",
        section="Clinical Profile",
        generic_name="Vancomycin",
        drug_class="Glycopeptide Antibiotic",
        indications="Treatment of severe Gram-positive infections including MRSA (Methicillin-Resistant Staphylococcus aureus), C. difficile-associated colitis (oral only), and penicillin-allergic patients.",
        contraindications="Known hypersensitivity to vancomycin.",
        mechanism="Inhibits bacterial cell wall synthesis by binding to the D-alanyl-D-alanine terminus of cell wall precursor units, preventing peptidoglycan polymerization and cell wall cross-linking.",
        dosing="IV dosing based on weight and renal function. Loading dose: 20-25 mg/kg. Maintenance: 15-20 mg/kg every 8-12 hours. Continuous infusion option exists.",
        renal_adjustment="Highly required: Dosing frequency is lengthened based on GFR. For GFR 30-50 mL/min: dose every 24 hours; GFR 15-29 mL/min: dose every 24-48 hours; GFR < 15/dialysis: dose based on serum trough levels/AUC.",
        monitoring="Renal function (BUN/creatinine), trough levels, or AUC-guided monitoring (target AUC/MIC ratio of 400-600, or troughs 15-20 mcg/mL for severe MRSA infections).",
        adverse_effects="Nephrotoxicity (dose-dependent, synergistic with piperacillin/tazobactam), ototoxicity, Red Man Syndrome (infusion reaction characterized by flushing/pruritus due to rapid histamine release), neutropenia.",
        interactions="Other nephrotoxins (aminoglycosides, loop diuretics, NSAIDs, piperacillin/tazobactam), anesthetic agents (increased risk of infusion reaction/hypotension).",
        tags=["vancomycin", "glycopeptide", "antibiotic", "MRSA", "renal adjustment", "troughs", "nephrotoxicity", "red man syndrome"],
        content=_build_content(
            generic_name="Vancomycin",
            drug_class="Glycopeptide Antibiotic",
            indications="Treatment of severe Gram-positive infections including MRSA (Methicillin-Resistant Staphylococcus aureus), C. difficile-associated colitis (oral only), and penicillin-allergic patients.",
            contraindications="Known hypersensitivity to vancomycin.",
            mechanism="Inhibits bacterial cell wall synthesis by binding to the D-alanyl-D-alanine terminus of cell wall precursor units, preventing peptidoglycan polymerization and cell wall cross-linking.",
            dosing="IV dosing based on weight and renal function. Loading dose: 20-25 mg/kg. Maintenance: 15-20 mg/kg every 8-12 hours. Continuous infusion option exists.",
            renal_adjustment="Highly required: Dosing frequency is lengthened based on GFR. For GFR 30-50 mL/min: dose every 24 hours; GFR 15-29 mL/min: dose every 24-48 hours; GFR < 15/dialysis: dose based on serum trough levels/AUC.",
            monitoring="Renal function (BUN/creatinine), trough levels, or AUC-guided monitoring (target AUC/MIC ratio of 400-600, or troughs 15-20 mcg/mL for severe MRSA infections).",
            adverse_effects="Nephrotoxicity (dose-dependent, synergistic with piperacillin/tazobactam), ototoxicity, Red Man Syndrome (infusion reaction characterized by flushing/pruritus due to rapid histamine release), neutropenia.",
            interactions="Other nephrotoxins (aminoglycosides, loop diuretics, NSAIDs, piperacillin/tazobactam), anesthetic agents (increased risk of infusion reaction/hypotension)."
        )
    ),
    ClinicalDocument(
        id="drug-furosemide",
        title="Furosemide Clinical Profile",
        source="FDA / ACC/AHA HF Guidelines",
        category="Drug",
        section="Clinical Profile",
        generic_name="Furosemide",
        drug_class="Loop Diuretic",
        indications="Edema associated with heart failure, renal disease (including acute kidney injury/renal failure), or hepatic disease. Also used for acute pulmonary edema.",
        contraindications="Anuria, severe hypersensitivity to furosemide or sulfonylureas (cross-sensitivity).",
        mechanism="Inhibits the absorption of sodium and chloride in the ascending limb of the loop of Henle by blocking the Na+/K+/2Cl- cotransporter, leading to increased excretion of water, sodium, chloride, potassium, and magnesium.",
        dosing="IV bolus: 20-40 mg over 1-2 minutes. Continuous IV infusion: 10-40 mg/hour. Critically ill patients with volume overload may require higher doses.",
        renal_adjustment="No renal dose adjustment required, but patients with advanced renal failure/low GFR may require significantly larger doses to achieve therapeutic diuretic effect.",
        monitoring="Daily weights, fluid balance, serum electrolytes (especially potassium, sodium, magnesium), BUN/creatinine, blood pressure (risk of hypotension), hearing (ototoxicity with rapid IV injection).",
        adverse_effects="Hypokalemia, hyponatremia, hypomagnesemia, prerenal azotemia (dehydration), hypotension, metabolic alkalosis, ototoxicity (tinnitus, hearing loss), hyperuricemia.",
        interactions="Other ototoxic drugs (aminoglycosides), other nephrotoxic drugs, lithium (furosemide increases lithium levels/toxicity), NSAIDs (decrease diuretic efficacy).",
        tags=["furosemide", "loop diuretic", "lasix", "diuresis", "hypokalemia", "fluid balance", "ototoxicity", "edema"],
        content=_build_content(
            generic_name="Furosemide",
            drug_class="Loop Diuretic",
            indications="Edema associated with heart failure, renal disease (including acute kidney injury/renal failure), or hepatic disease. Also used for acute pulmonary edema.",
            contraindications="Anuria, severe hypersensitivity to furosemide or sulfonylureas (cross-sensitivity).",
            mechanism="Inhibits the absorption of sodium and chloride in the ascending limb of the loop of Henle by blocking the Na+/K+/2Cl- cotransporter, leading to increased excretion of water, sodium, chloride, potassium, and magnesium.",
            dosing="IV bolus: 20-40 mg over 1-2 minutes. Continuous IV infusion: 10-40 mg/hour. Critically ill patients with volume overload may require higher doses.",
            renal_adjustment="No renal dose adjustment required, but patients with advanced renal failure/low GFR may require significantly larger doses to achieve therapeutic diuretic effect.",
            monitoring="Daily weights, fluid balance, serum electrolytes (especially potassium, sodium, magnesium), BUN/creatinine, blood pressure (risk of hypotension), hearing (ototoxicity with rapid IV injection).",
            adverse_effects="Hypokalemia, hyponatremia, hypomagnesemia, prerenal azotemia (dehydration), hypotension, metabolic alkalosis, ototoxicity (tinnitus, hearing loss), hyperuricemia.",
            interactions="Other ototoxic drugs (aminoglycosides), other nephrotoxic drugs, lithium (furosemide increases lithium levels/toxicity), NSAIDs (decrease diuretic efficacy)."
        )
    )
]
