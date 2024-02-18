import Accordion from "../../components/schedules/accordion";

import { getUserSchedules } from "@/app/utils/schedules";
import { getCookie } from "cookies-next";
import { cookies } from "next/headers";

export default async function Schedules() {
  const accessToken = getCookie("accessToken", { cookies });
  const userSchedules = await getUserSchedules(accessToken);
  return (
    <div className="p-4 sm:ml-64">
      <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
        <div className="grid w-full grid-cols-1 gap-4 mt-4 xl:grid-cols-2 mb-4">
          {/* List of all schedules */}
          <Accordion schedules={userSchedules}></Accordion>
          {/* Edit schedule */}
          <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800 xl:max-h-[65vh] xl:overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Edit schedule
              </h3>
            </div>
            <ul
              role="list"
              className="divide-y divide-gray-200 dark:divide-gray-700"
            >
              <li></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
