import {
  Activity,
  AlertTriangle,
  BedDouble,
  Brain,
  HeartPulse,
  ShieldAlert,
  Users,
} from "lucide-react";

export const dashboardStats = [
  {
    id: 1,
    title: "ICU Patients",
    value: 48,
    change: "+5.4%",
    trend: "up",
    color: "blue",
    icon: Users,
  },
  {
    id: 2,
    title: "Critical Cases",
    value: 12,
    change: "-2.1%",
    trend: "down",
    color: "red",
    icon: ShieldAlert,
  },
  {
    id: 3,
    title: "Bed Occupancy",
    value: "86%",
    change: "+3%",
    trend: "up",
    color: "emerald",
    icon: BedDouble,
  },
  {
    id: 4,
    title: "AI Alerts",
    value: 7,
    change: "+1",
    trend: "up",
    color: "amber",
    icon: AlertTriangle,
  },
];

export const aiSummary = {
  risk: "HIGH",
  confidence: 97,
  prediction: "High probability of Sepsis detected.",
  recommendation:
    "Administer broad-spectrum antibiotics within one hour. Monitor lactate levels and begin fluid resuscitation.",
};

export const aiStatus = {
  llm: "Online",
  rag: "Connected",
  prediction: "Running",
  knowledgeBase: "1,248 Medical Documents",
};

export const recentPatients = [
  {
    id: "ICU-1001",
    name: "Amelia Chen",
    risk: "HIGH",
    heartRate: 118,
    spo2: "91%",
  },
  {
    id: "ICU-1002",
    name: "John Smith",
    risk: "MEDIUM",
    heartRate: 97,
    spo2: "96%",
  },
  {
    id: "ICU-1003",
    name: "Sophia Wilson",
    risk: "LOW",
    heartRate: 81,
    spo2: "99%",
  },
];