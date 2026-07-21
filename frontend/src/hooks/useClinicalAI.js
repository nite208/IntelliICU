import { useState } from "react";
import { aiService } from "../services/aiService";

export function useClinicalAI() {
  const [loading, setLoading] = useState(false);
  const [recommendation, setRecommendation] = useState(null);
  const [error, setError] = useState(null);

  async function analyze(payload) {
    try {
      setLoading(true);
      setError(null);

      const data = await aiService.analyzePatient(payload);

      setRecommendation(data);

      return data;
    } catch (err) {
      console.error(err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }

  return {
    loading,
    recommendation,
    error,
    analyze,
  };
}