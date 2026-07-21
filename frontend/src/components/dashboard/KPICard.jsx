import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { motion } from "framer-motion";

export default function KPICard({

    title,
    value,
    change,
    trend,
    icon: Icon,
    color,

}) {

    const colors = {

        blue:"bg-blue-50 text-blue-600",

        emerald:"bg-emerald-50 text-emerald-600",

        red:"bg-red-50 text-red-600",

        amber:"bg-amber-50 text-amber-600"

    };

    return(

        <motion.div

        whileHover={{

            y:-6,

            scale:1.02

        }}

        className="rounded-3xl bg-white border border-slate-200 shadow-sm p-6 cursor-pointer"

        >

            <div className="flex justify-between">

                <div>

                    <p className="text-slate-500">

                        {title}

                    </p>

                    <h1 className="mt-3 text-5xl font-black">

                        {value}

                    </h1>

                </div>

                <div className={`h-16 w-16 rounded-2xl flex items-center justify-center ${colors[color]}`}>

                    <Icon size={30}/>

                </div>

            </div>

            <div className="mt-8 flex items-center justify-between">

                <span className="text-slate-400">

                    Last 24 Hours

                </span>

                <div className={`flex items-center gap-1 ${trend==="up"?"text-emerald-600":"text-red-500"}`}>

                    {

                        trend==="up"

                        ?

                        <ArrowUpRight size={18}/>

                        :

                        <ArrowDownRight size={18}/>

                    }

                    {change}

                </div>

            </div>

        </motion.div>

    );

}