"use client";

import { getCookie } from "cookies-next";
import { FormEvent } from "react";

type Props = {
  adhocScanFunc: any;
}

export default async function NewSearch({adhocScanFunc}: Props) {
  function addNewSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const url = formData.get("url");
    const day = formData.get("day");
    const hour = formData.get("hour");
    const minute = formData.get("minute");
    const accessToken = getCookie("accessToken")
    adhocScanFunc({url, day, hour, minute}, accessToken)
    const form = (document.getElementById("newSearchForm") as HTMLFormElement)
    form.reset();
  }
  return (
    <>
      <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm w-full dark:border-gray-700 sm:p-6 dark:bg-gray-800">
        <div className="items-center justify-between flex">
          <div className="mb-4 lg:mb-0">
            <h3 className="mb-3 text-xl font-medium text-gray-900 dark:text-white">
              Register a new search
            </h3>
            <p className="mb-5 text-sm font-medium text-gray-500 dark:text-gray-300">
              Do you want to add a new search? Copy and paste search link from
              provider portal. Decide about scan schedule. Adding new search
              will automatically trigger adhoc scan.
            </p>
            <form id="newSearchForm" onSubmit={addNewSearch}>
              <div className="relative mb-7">
                <input
                  type="url"
                  id="url"
                  name="url"
                  className="block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
                  placeholder=" "
                  required
                />
                <label
                  htmlFor="url"
                  className="absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white dark:bg-gray-900 px-2 peer-focus:px-2 peer-focus:text-blue-600 peer-focus:dark:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto start-1"
                >
                  Search URL
                </label>
              </div>

              <div className="grid gap-6 mb-6 md:grid-cols-3">
                <div className="relative">
                  <select
                    id="day"
                    name="day"
                    className="block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
                  >
                    <option value="0">Sunday</option>
                    <option value="1">Monday</option>
                    <option value="2">Tuesday</option>
                    <option value="3">Wednesday</option>
                    <option value="4">Thursday</option>
                    <option value="5">Friday</option>
                    <option value="6">Saturday</option>
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
                    {[
                      ...Array.from({ length: 24 }, (value, index) => index),
                    ].map((hour) => {
                      return (
                        <option value={hour} key={hour}>
                          {hour}
                        </option>
                      );
                    })}
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
                    {[
                      ...Array.from({ length: 60 }, (value, index) => index),
                    ].map((minute) => {
                      return (
                        <option value={minute} key={minute}>
                          {minute}
                        </option>
                      );
                    })}
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
                Add new search
              </button>
            </form>
          </div>
        </div>
      </div>
      <script type="text/javascript"></script>
    </>
  );
}
