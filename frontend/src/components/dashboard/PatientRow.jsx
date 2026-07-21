import { MoreHorizontal } from "lucide-react";

export default function PatientRow({ patient }) {

  const statusColor = {
    Critical: "bg-red-100 text-red-700",
    Serious: "bg-amber-100 text-amber-700",
    Stable: "bg-emerald-100 text-emerald-700",
  };

  const riskColor = {
    High: "text-red-600",
    Medium: "text-amber-600",
    Low: "text-emerald-600",
  };

  return (
    <tr className="hover:bg-slate-50 transition">

      <td className="py-4 font-medium">{patient.id}</td>

      <td>
        <div>
          <p className="font-semibold">{patient.name}</p>
          <p className="text-sm text-slate-500">
            {patient.age}y • {patient.diagnosis}
          </p>
        </div>
      </td>

      <td>{patient.bed}</td>

      <td>
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColor[patient.status]}`}
        >
          {patient.status}
        </span>
      </td>

      <td>
        <span className={`font-semibold ${riskColor[patient.risk]}`}>
          ● {patient.risk}
        </span>
      </td>

      <td>{patient.heartRate} bpm</td>

      <td>{patient.spo2}%</td>

      <td>{patient.bp}</td>

      <td>
        <button className="hover:bg-slate-100 rounded-lg p-2">
          <MoreHorizontal size={18} />
        </button>
      </td>

    </tr>
  );
}