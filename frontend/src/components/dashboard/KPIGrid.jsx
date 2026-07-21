import KPICard from "./KPICard";

import {

dashboardStats

}

from "../../assets/data/dashboardData";

export default function KPIGrid(){

    return(

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

            {

                dashboardStats.map((item)=>(

                    <KPICard

                    key={item.id}

                    {...item}

                    />

                ))

            }

        </div>

    );

}