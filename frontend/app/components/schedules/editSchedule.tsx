"use client";

import { FormEvent } from "react";

type Props = {
  search: {
    category: { name: string };
    distanceRadius: number;
    id: number;
    location: string;
    schedule?: { dayOfWeek: number; hour: number; minute: number };
  };
  editScheduleFunc: any
};

export default async function EditSchedule({ search, editScheduleFunc }: Props) {
    function editSchedule(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);
        const day = formData.get("day");
        const hour = formData.get("hour");
        const minute = formData.get("minute");
        editScheduleFunc(search.id, day, hour, minute)
    }
  return (
    <>
      <p className="mb-5 text-sm font-medium text-gray-500 dark:text-gray-300">
        {search.location}; {search.distanceRadius} km
      </p>
      <form onSubmit={editSchedule}>
        <div className="grid gap-6 mb-6 md:grid-cols-3">
          <div className="relative">
            <select
              id="day"
              name="day"
              className="block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            >
              <option value="0">Sunday</option>
              <option value="1" selected={search.schedule?.dayOfWeek == 1 ? true : false}>Monday</option>
              <option value="2" selected={search.schedule?.dayOfWeek == 2 ? true : false}>Tuesday</option>
              <option value="3" selected={search.schedule?.dayOfWeek == 3 ? true : false}>Wednesday</option>
              <option value="4" selected={search.schedule?.dayOfWeek == 4 ? true : false}>Thursday</option>
              <option value="5" selected={search.schedule?.dayOfWeek == 5 ? true : false}>Friday</option>
              <option value="6" selected={search.schedule?.dayOfWeek == 6 ? true : false}>Saturday</option>
            </select>
            <label
              htmlFor="day"
              className="absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white dark:bg-gray-900 px-2 peer-focus:px-2 peer-focus:text-blue-600 peer-focus:dark:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto start-1"
            >
              Day of the week
            </label>
          </div>
          <div className="relative">
            <select
              id="hour"
              name="hour"
              className="block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            >
              {[...Array.from({ length: 24 }, (value, index) => index)].map(
                (hour) => {
                  return (
                    <option value={hour} key={hour} selected={search.schedule?.hour == hour ? true : false}>
                      {hour}
                    </option>
                  );
                }
              )}
            </select>
            <label
              htmlFor="hour"
              className="absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white dark:bg-gray-900 px-2 peer-focus:px-2 peer-focus:text-blue-600 peer-focus:dark:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto start-1"
            >
              Hour
            </label>
          </div>
          <div className="relative">
            <select
              id="minute"
              name="minute"
              className="block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            >
              {[...Array.from({ length: 60 }, (value, index) => index)].map(
                (minute) => {
                  return (
                    <option value={minute} key={minute} selected={search.schedule?.minute == minute ? true : false}>
                      {minute}
                    </option>
                  );
                }
              )}
            </select>
            <label
              htmlFor="hour"
              className="absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white dark:bg-gray-900 px-2 peer-focus:px-2 peer-focus:text-blue-600 peer-focus:dark:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto start-1"
            >
              Minute
            </label>
          </div>
        </div>
        <button
          type="submit"
          className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
        >
          Edit Schedule
        </button>
      </form>
    </>
  );
}
