import { CheckCircle2 } from "lucide-react";
import { clinicalTasks } from "../../assets/data/alertsData";

export default function ClinicalTasks(){

  return(

    <div className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6">

      <h2 className="text-xl font-bold mb-6">

        Clinical Tasks

      </h2>

      <div className="space-y-4">

        {

          clinicalTasks.map((task,index)=>(

            <button

              key={index}

              className="w-full rounded-xl border p-4 text-left hover:bg-cyan-50 transition"

            >

              <div className="flex justify-between items-center">

                <span>

                  {task}

                </span>

                <CheckCircle2 className="text-cyan-600"/>

              </div>

            </button>

          ))

        }

      </div>

    </div>

  );

}