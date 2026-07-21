import { patients } from "../../assets/data/patientsData";
import PatientRow from "./PatientRow";

export default function RecentPatientsTable() {

  return (

    <div className="bg-white rounded-3xl border border-slate-200 shadow-sm">

      <div className="flex items-center justify-between p-6">

        <div>

          <h2 className="text-2xl font-bold">
            Recent Patients
          </h2>

          <p className="text-slate-500">
            Live ICU census • Updated just now
          </p>

        </div>

        <button className="text-cyan-600 font-semibold hover:underline">
          View All
        </button>

      </div>

      <div className="overflow-x-auto">

        <table className="w-full">

          <thead className="border-y bg-slate-50">

            <tr className="text-left text-sm text-slate-500">

              <th className="py-4 px-6">Patient ID</th>
              <th>Name</th>
              <th>Bed</th>
              <th>Status</th>
              <th>Risk</th>
              <th>HR</th>
              <th>SpO₂</th>
              <th>BP</th>
              <th></th>

            </tr>

          </thead>

          <tbody>

            {patients.map(patient => (

              <PatientRow
                key={patient.id}
                patient={patient}
              />

            ))}

          </tbody>

        </table>

      </div>

    </div>

  );

}