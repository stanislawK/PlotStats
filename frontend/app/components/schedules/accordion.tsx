"use client";

import Day from "./day";

type Props = {
  schedules: {
    Monday: {};
    Tuesday: {};
    Wednesday: {};
    Thursday: {};
    Friday: {};
    Saturday: {};
    Sunday: {};
    disabled?: [];
  };
};

export default async function SchedulesAccordion({ schedules }: Props) {
  const disabled = schedules.disabled;
  delete schedules.disabled;
  return (
    <>
      <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800 xl:max-h-[65vh] xl:overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            All schedules
          </h3>
        </div>
        {Object.entries(schedules).map(([name, schedule]) => {
          return <Day name={name} schedule={schedule} key={name}></Day>;
        })}
      </div>
    </>
  );
}
