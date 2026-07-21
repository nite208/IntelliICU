"""
Recommendation Engine Service
"""

class RecommendationEngine:
    """
    Enterprise AI Recommendation Engine (Rule-Based).
    Generates evidence-based recommendations for ICU clinicians.
    """

    @staticmethod
    def generate(patient_data: dict) -> list[dict]:
        """
        Generate recommendations based on:
        - risk_score
        - SpO2
        - temperature
        - systolic_bp
        - lactate
        """
        recommendations = []

        # Helper to safely parse numeric values (handling optional nesting and string units)
        def get_value(keys, default=None):
            # Keys can be a list of keys representing a path, or a single key string
            for key_path in keys if isinstance(keys[0], list) else [keys]:
                val = patient_data
                for k in key_path:
                    if isinstance(val, dict):
                        val = val.get(k)
                    else:
                        val = None
                        break
                if val is not None:
                    # Clean and parse value
                    if isinstance(val, (int, float)):
                        return float(val)
                    if isinstance(val, str):
                        import re
                        match = re.search(r"[-+]?\d*\.\d+|\d+", val)
                        if match:
                            return float(match.group())
            return default

        # Extract values
        # risk_score: can be in flat patient dict or nested under 'patient' or 'ai' or 'prediction'
        risk_score = get_value([["patient", "risk_score"], ["prediction", "risk_score"], ["risk_score"]], None)
        
        # spo2: can be under 'vitals' or flat 'spo2'
        spo2 = get_value([["vitals", "spo2"], ["spo2"]], None)
        
        # temperature: can be under 'vitals' or flat 'temperature'
        temp = get_value([["vitals", "temperature"], ["temperature"]], None)
        
        # systolic_bp: under vitals -> blood_pressure -> systolic, or vitals -> systolic_bp, or flat 'systolic_bp'
        systolic_bp = get_value([
            ["vitals", "blood_pressure", "systolic"],
            ["vitals", "systolic_bp"],
            ["systolic_bp"]
        ], None)
        
        # lactate: under labs -> Lactate, or labs -> lactate, or flat 'lactate'
        lactate = get_value([
            ["labs", "Lactate"],
            ["labs", "lactate"],
            ["lactate"]
        ], None)

        # Generate Rule-Based Sepsis Risk Recommendations
        if risk_score is not None:
            if risk_score >= 0.80:
                recommendations.append({
                    "priority": "HIGH",
                    "title": "Critical Sepsis Risk Alert",
                    "description": f"Sepsis probability is critical ({risk_score * 100:.1f}%). Initiate full sepsis protocol, obtain blood cultures, and administer broad-spectrum antibiotics within 1 hour."
                })
            elif risk_score >= 0.50:
                recommendations.append({
                    "priority": "MEDIUM",
                    "title": "Elevated Sepsis Risk",
                    "description": f"Patient has a moderate risk of sepsis ({risk_score * 100:.1f}%). Monitor vital signs hourly and assess for signs of organ dysfunction."
                })

        # Generate Rule-Based SpO2 Recommendations
        if spo2 is not None:
            if spo2 < 90:
                recommendations.append({
                    "priority": "HIGH",
                    "title": "Critical Hypoxemia",
                    "description": f"SpO₂ is low ({spo2}%). Increase oxygen flow rate, consider non-invasive ventilation (NIV), and monitor arterial blood gas (ABG) values."
                })
            elif spo2 < 94:
                recommendations.append({
                    "priority": "MEDIUM",
                    "title": "Mild Hypoxemia",
                    "description": f"SpO₂ is borderline ({spo2}%). Ensure proper patient positioning, maintain target oxygen saturation, and monitor respiratory effort."
                })

        # Generate Rule-Based Systolic BP Recommendations
        if systolic_bp is not None:
            if systolic_bp < 90:
                recommendations.append({
                    "priority": "HIGH",
                    "title": "Severe Hypotension",
                    "description": f"Systolic blood pressure is critically low ({systolic_bp} mmHg). Initiate fluid resuscitation (30 mL/kg crystalloid) or adjust vasopressor support to target MAP > 65 mmHg."
                })
            elif systolic_bp < 100:
                recommendations.append({
                    "priority": "MEDIUM",
                    "title": "Borderline Hypotension",
                    "description": f"Systolic blood pressure is low-normal ({systolic_bp} mmHg). Monitor fluid balance and adjust vasopressor infusion rates as indicated."
                })

        # Generate Rule-Based Lactate Recommendations
        if lactate is not None:
            if lactate >= 4.0:
                recommendations.append({
                    "priority": "HIGH",
                    "title": "Critical Hyperlactatemia",
                    "description": f"Lactate is critically high ({lactate} mmol/L), indicating severe tissue hypoperfusion. Follow the resuscitation bundle and repeat lactate measurement in 2 hours."
                })
            elif lactate >= 2.0:
                recommendations.append({
                    "priority": "MEDIUM",
                    "title": "Elevated Blood Lactate",
                    "description": f"Lactate is elevated ({lactate} mmol/L). Monitor perfusion indicators and repeat lactate in 4 hours to verify clearance."
                })

        # Generate Rule-Based Temperature Recommendations
        if temp is not None:
            if temp >= 39.0:
                recommendations.append({
                    "priority": "HIGH",
                    "title": "Severe Hyperthermia",
                    "description": f"Core temperature is critically high ({temp}°C). Administer antipyretics, consider cooling blankets, and ensure adequate fluid volume."
                })
            elif temp > 38.3:
                recommendations.append({
                    "priority": "MEDIUM",
                    "title": "Febrile Episode",
                    "description": f"Fever detected ({temp}°C). Obtain blood, urine, or sputum cultures if new-onset infection is suspected, and monitor temperature trends."
                })
            elif temp < 36.0:
                recommendations.append({
                    "priority": "HIGH",
                    "title": "Hypothermia Alert",
                    "description": f"Core temperature is low ({temp}°C). Apply passive or active external rewarming methods and monitor temperature hourly."
                })

        # If no specific rule triggered, return default clinical workspace recommendations
        if not recommendations:
            recommendations.append({
                "priority": "LOW",
                "title": "Standard Monitoring",
                "description": "Maintain standard ICU monitoring protocol, document vital signs hourly, and track fluid intake/output."
            })

        return recommendations
