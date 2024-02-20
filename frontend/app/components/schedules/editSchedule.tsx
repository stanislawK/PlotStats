"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

type Props = {
  search: {
    category: { name: string };
    distanceRadius: number;
    id: number;
    location: string;
    schedule?: { dayOfWeek: number; hour: number; minute: number };
  };
  editScheduleFunc: any;
  disableScheduleFunc: any;
};

export default function EditSchedule({
  search,
  editScheduleFunc,
  disableScheduleFunc,
}: Props) {
  function editSchedule(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const day = formData.get("day");
    const hour = formData.get("hour");
    const minute = formData.get("minute");
    editScheduleFunc(search.id, day, hour, minute);
  }
  function disableSchedule() {
    disableScheduleFunc(search.id);
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
              defaultValue={search.schedule?.dayOfWeek}
              key={search.schedule?.dayOfWeek}
            >
              <option value="0" key="0">
                Sunday
              </option>
              <option value="1" key="1">
                Monday
              </option>
              <option value="2" key="2">
                Tuesday
              </option>
              <option value="3" key="3">
                Wednesday
              </option>
              <option value="4" key="4">
                Thursday
              </option>
              <option value="5" key="5">
                Friday
              </option>
              <option value="6" key="6">
                Saturday
              </option>
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
              defaultValue={search.schedule?.hour}
              key={search.schedule?.hour}
              className="block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            >
              {[...Array.from({ length: 24 }, (value, index) => index)].map(
                (hour) => {
                  return (
                    <option value={hour} key={hour}>
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
              defaultValue={search.schedule?.minute}
              key={search.schedule?.minute}
              className="block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
            >
              {[...Array.from({ length: 60 }, (value, index) => index)].map(
                (minute) => {
                  return (
                    <option value={minute} key={minute}>
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
        <div className="flex flex-row space-x-3">
          <button
            type="submit"
            className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 inline-flex items-center"
          >
            {!!search.schedule ? "Edit" : "Add"} Schedule
          </button>
          {!!search.schedule && (
            <Link href={`schedules`}>
              <button
                type="button"
                onClick={disableSchedule}
                className="text-white bg-red-600 hover:bg-red-700 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-red-300 dark:hover:bg-red-400 dark:focus:ring-red-700 inline-flex items-center"
              >
                <svg
                  className="w-4 h-4 text-white me-2"
                  aria-hidden="true"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke="currentColor"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 7h14m-9 3v8m4-8v8M10 3h4a1 1 0 0 1 1 1v3H9V4a1 1 0 0 1 1-1ZM6 7h12v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7Z"
                  />
                </svg>
                Disable Schedule
              </button>
            </Link>
          )}
        </div>
      </form>
    </>
  );
}
