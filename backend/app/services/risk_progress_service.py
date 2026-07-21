"""
Risk Progress Engine Service
"""

class RiskProgressEngine:
    """
    Enterprise Risk Progress Engine.
    Dynamically calculates current risk, previous risk, change, and risk trend based on patient data and history.
    """

    @staticmethod
    def generate(patient_data: dict) -> dict:
        """
        Calculates:
        - current_risk
        - previous_risk
        - change
        - trend (Increasing/Stable/Decreasing)
        """
        # Helper to safely parse numeric values
        def get_value(keys, default=0.5):
            for key_path in keys if isinstance(keys[0], list) else [keys]:
                val = patient_data
                for k in key_path:
                    if isinstance(val, dict):
                        val = val.get(k)
                    else:
                        val = None
                        break
                if val is not None:
                    if isinstance(val, (int, float)):
                        return float(val)
                    if isinstance(val, str):
                        import re
                        match = re.search(r"[-+]?\d*\.\d+|\d+", val)
                        if match:
                            return float(match.group())
            return default

        current_risk = round(get_value([["patient", "risk_score"], ["prediction", "risk_score"], ["risk_score"]], 0.5), 2)

        # Let's inspect history to dynamically calculate trend and previous risk
        history = patient_data.get("history", [])
        trend = "Stable"
        delta = 0.0

        if len(history) >= 2:
            first = history[0]
            last = history[-1]

            worsening_factors = 0
            improving_factors = 0

            # Compare Heart Rate
            hr_first = first.get("heart_rate") or first.get("hr")
            hr_last = last.get("heart_rate") or last.get("hr")
            if hr_first is not None and hr_last is not None:
                if hr_last > hr_first:
                    worsening_factors += 1
                elif hr_last < hr_first:
                    improving_factors += 1

            # Compare SpO2
            spo2_first = first.get("spo2")
            spo2_last = last.get("spo2")
            if spo2_first is not None and spo2_last is not None:
                if spo2_last < spo2_first:
                    worsening_factors += 1
                elif spo2_last > spo2_first:
                    improving_factors += 1

            # Compare Temperature
            temp_first = first.get("temperature") or first.get("temp")
            temp_last = last.get("temperature") or last.get("temp")
            if temp_first is not None and temp_last is not None:
                if temp_last > temp_first:
                    worsening_factors += 1
                elif temp_last < temp_first:
                    improving_factors += 1

            # Compare MAP
            map_first = first.get("map") or first.get("mean_arterial_pressure")
            map_last = last.get("map") or last.get("mean_arterial_pressure")
            if map_first is not None and map_last is not None:
                if map_last < map_first:
                    worsening_factors += 1
                elif map_last > map_first:
                    improving_factors += 1

            # Determine trend and delta
            if worsening_factors > improving_factors:
                trend = "Increasing"
                delta = 0.01 * (worsening_factors - improving_factors) + 0.03
            elif improving_factors > worsening_factors:
                trend = "Decreasing"
                delta = - (0.01 * (improving_factors - worsening_factors) + 0.03)
            else:
                trend = "Stable"
                delta = 0.0

        change = round(abs(delta), 2)

        if trend == "Increasing":
            previous_risk = round(max(0.0, current_risk - change), 2)
        elif trend == "Decreasing":
            previous_risk = round(min(1.0, current_risk + change), 2)
        else:
            previous_risk = current_risk

        return {
            "current_risk": current_risk,
            "previous_risk": previous_risk,
            "change": change,
            "trend": trend
        }
