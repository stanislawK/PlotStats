"use client";

import { Disclosure } from "@headlessui/react";
import TimeEntry from "./timeEntry";

type Props = {
  name: string;
  schedule: {
    Monday: {};
    Tuesday: {};
    Wednesday: {};
    Thursday: {};
    Friday: {};
    Saturday: {};
    Sunday: {};
    disabled: [];
  };
};

export default function Day({ name, schedule }: Props) {
  const timeStrings = Object.keys(schedule);
  timeStrings.sort();
  if (timeStrings.length === 0) {
    return;
  }
  return (
    <Disclosure as="div" className="mt-2" defaultOpen>
      {({ open }) => (
        <>
          <Disclosure.Button className="group font-semibold text-base flex w-full justify-between rounded-lg bg-slate-50 border-b px-4 py-2 text-left hover:text-white hover:bg-blue-700 focus:outline-none focus-visible:ring focus-visible:ring-blue-300">
            <span>{name}</span>
            <svg
              className={`${
                open ? "rotate-180 transform" : ""
              } w-6 h-6 text-gray-800 dark:text-white group-hover:text-white`}
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
                d="m5 15 7-7 7 7"
              />
            </svg>
          </Disclosure.Button>
          <Disclosure.Panel className="px-2 pb-2 pt-4 text-sm text-gray-500">
            <div className="flow-root my-2">
              <div className="-my-4 divide-y divide-gray-200 dark:divide-gray-700">
                {timeStrings.map((time) => {
                  return (
                    <TimeEntry
                      time={time}
                      // @ts-ignore
                      searches={schedule[time]}
                      key={`${time}${new Date().getTime()}`}
                    ></TimeEntry>
                  );
                })}
              </div>
            </div>
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}
