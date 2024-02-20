"use client";

import Link from "next/link";
import CategoryIcon from "../ui/categoryIcon";

type Props = {
  time: string;
  searches: {
    category: {
      name: string;
    };
    distanceRadius: number;
    id: number;
    location: string;
    schedule: {
      dayOfWeek: number;
      hour: number;
      minute: number;
    };
  }[];
};

export default function TimeEntry({ time, searches }: Props) {
  return (
    <>
      {searches.map((search) => {
        return (
          <div
            className="flex flex-col gap-2 py-4 sm:gap-6 sm:flex-row sm:items-center"
            key={search.id}
          >
            <p className="w-32 font-normal text-gray-500 ml-2 lg:ml-4 dark:text-gray-400 shrink-0">
              {time}
            </p>
            <div className="flex-shrink-0">
              <CategoryIcon
                category={search.category.name}
                key={search.id}
              ></CategoryIcon>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {search.location}; {search.distanceRadius} km
            </h3>
            <Link href={`schedules/?search=${search.id}`} className="ml-auto">
              <svg
                className="w-6 h-6 text-gray-800 dark:text-white hover:text-green-500"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="1"
                  d="m14.3 4.8 2.9 2.9M7 7H4a1 1 0 0 0-1 1v10c0 .6.4 1 1 1h11c.6 0 1-.4 1-1v-4.5m2.4-10a2 2 0 0 1 0 3l-6.8 6.8L8 14l.7-3.6 6.9-6.8a2 2 0 0 1 2.8 0Z"
                />
              </svg>
            </Link>
          </div>
        );
      })}
    </>
  );
}
