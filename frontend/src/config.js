const isProduction = import.meta.env.PROD;

const hostname =
  typeof window !== "undefined"
    ? window.location.hostname
    : "localhost";

const protocol =
  typeof window !== "undefined"
    ? window.location.protocol
    : "http:";

const wsProtocol =
  protocol === "https:" ? "wss:" : "ws:";

/*
 * IntelliICU Environment Configuration
 *
 * Production:
 *   Uses Railway backend URLs.
 *
 * Development:
 *   Uses VITE environment variables when available,
 *   otherwise falls back to localhost:8000.
 */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  (isProduction
    ? "https://intelliicu-production.up.railway.app/api"
    : `${protocol}//${hostname}:8000/api`);

const WS_BASE_URL =
  import.meta.env.VITE_WS_BASE_URL ||
  (isProduction
    ? "wss://intelliicu-production.up.railway.app/ws"
    : `${wsProtocol}//${hostname}:8000/ws`);

const config = {
  API_BASE_URL,
  WS_BASE_URL,

  ESCALATION_L2_SECONDS: 15,
  ESCALATION_L3_SECONDS: 30,
};

export default config;