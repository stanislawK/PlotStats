import Accordion from "../../components/schedules/accordion";
import EditSchedule from "@/app/components/schedules/editSchedule";
import DisabledList from "@/app/components/schedules/disabledList";

import {
  getUserSchedules,
  parseSchedules,
  findSearchById,
  editSchedule,
  disableSchedule,
} from "@/app/utils/schedules";
import { getCookie } from "cookies-next";
import { revalidatePath } from "next/cache";
import { cookies } from "next/headers";

type Props = {
  searchParams: Record<string, string> | null | undefined;
};

export default async function Schedules({ searchParams }: Props) {
  const accessToken = getCookie("accessToken", { cookies });
  // @ts-ignore
  const userSearches = await getUserSchedules(accessToken);
  const userSchedules = await parseSchedules(userSearches);
  const searchId = searchParams?.search;
  let searchToEdit;
  if (searchId !== undefined && !isNaN(parseInt(searchId))) {
    searchToEdit = await findSearchById(userSearches, parseInt(searchId));
  }
  const editScheduleFunc = async (
    id: number,
    day: number,
    hour: number,
    minute: number
  ) => {
    "use server";
    // @ts-ignore
    await editSchedule(accessToken, id, day, hour, minute);
    revalidatePath("/dashboard/schedules");
  };
  const disableScheduleFunc = async (id: number) => {
    "use server";
    // @ts-ignore
    await disableSchedule(accessToken, id);
  };
  // @ts-ignore
  const disabledExists = userSearches.some((search) => !search.schedule);
  return (
    <div className="p-4 sm:ml-64">
      <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
        <div className="grid w-full grid-cols-1 gap-4 mt-4 xl:grid-cols-2 mb-4">
          {/* List of all schedules */}
          <Accordion
            // @ts-ignore
            schedules={userSchedules}
          ></Accordion>
          {/* Edit schedule */}
          <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800 xl:max-h-[65vh] xl:overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Edit schedule
              </h3>
            </div>
            {!!searchToEdit && (
              <EditSchedule
                search={searchToEdit}
                editScheduleFunc={editScheduleFunc}
                disableScheduleFunc={disableScheduleFunc}
              />
            )}
          </div>
        </div>
        {disabledExists && (
          <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800">
            <DisabledList searches={userSearches}></DisabledList>
          </div>
        )}
      </div>
    </div>
  );
}
