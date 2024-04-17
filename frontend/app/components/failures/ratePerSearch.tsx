"use client";

import dynamic from "next/dynamic";
const ApexChart = dynamic(() => import("react-apexcharts"), { ssr: false });

type Props = {
  failures: Failure[];
  successes: Success[];
  searches: Search[];
};

type Failure = {
  searchId: number;
  failures: {
    date: string;
    status: number;
  }[];
};

type Success = {
  searchId: number;
  successes: string[];
};

type Search = {
  id: number;
  location: string;
};

type countsPerSearch = {
  [key: string]: { successes: number; failures: number };
};

const getSeriesData = (
  failures: Failure[],
  successes: Success[],
  searches: Search[]
): countsPerSearch => {
  const countsPerSearch: countsPerSearch = {};
  searches.forEach((search) => {
    const searchName = `${search.id}. ${search.location}`;
    const success = successes.find((success) => success.searchId == search.id);
    const successCount = !!success ? success.successes.length : 0;
    const failure = failures.find((failure) => failure.searchId == search.id);
    const failureCount = !!failure ? failure.failures.length : 0;
    if (successCount > 0 || failureCount > 0) {
      countsPerSearch[searchName] = {
        successes: successCount,
        failures: failureCount,
      };
    }
  });
  return countsPerSearch;
};

export default function RatePerSearchChart({
  failures,
  successes,
  searches,
}: Props) {
  const countsPerSearch = getSeriesData(failures, successes, searches);
  const successSeries = Object.keys(countsPerSearch).flatMap((searchName) => [
    { x: searchName, y: countsPerSearch[searchName].successes },
  ]);
  const failureSeries = Object.keys(countsPerSearch).flatMap((searchName) => [
    { x: searchName, y: countsPerSearch[searchName].failures },
  ]);
  const series = [
    {
      name: "Successes",
      color: "#32a852",
      data: successSeries,
    },
    {
      name: "Failures",
      color: "#a8323a",
      data: failureSeries,
    },
  ];
  const options = {
    colors: ["#32a852", "#a8323a"],
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: "70%",
        borderRadiusApplication: "end",
        borderRadius: 8,
      },
    },
    tooltip: {
      shared: true,
      intersect: false,
      style: {
        fontFamily: "Inter, sans-serif",
      },
    },
    states: {
      hover: {
        filter: {
          type: "darken",
          value: 1,
        },
      },
    },
    stroke: {
      show: true,
      width: 0,
      colors: ["transparent"],
    },
    grid: {
      show: false,
      strokeDashArray: 4,
      padding: {
        left: 2,
        right: 2,
        top: -14,
      },
    },
    dataLabels: {
      enabled: false,
    },
    legend: {
      show: false,
    },
    xaxis: {
      categories: Object.keys(countsPerSearch),
      floating: false,
      labels: {
        show: true,
        style: {
          fontFamily: "Inter, sans-serif",
          cssClass: "text-xs font-normal fill-gray-500 dark:fill-gray-400",
        },
      },
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
    },
    yaxis: {
      show: false,
    },
    fill: {
      opacity: 1,
    },
  };

  return (
    <>
      <div className="w-full bg-white rounded-lg shadow dark:bg-gray-800 p-4 md:p-6">
        <div className="flex justify-between pb-4 mb-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div>
              <h5 className="leading-none text-2xl font-bold text-gray-900 dark:text-white pb-1">
                Rates per search
              </h5>
              <p className="text-sm font-normal text-gray-500 dark:text-gray-400">
                Success/failure rates per every search in last 30 days
              </p>
            </div>
          </div>
        </div>

        <div id="column-chart">
          <ApexChart
            options={options}
            series={series}
            height={420}
            width="100%"
            type="bar"
          ></ApexChart>
        </div>
        <div className="grid grid-cols-1 items-center border-gray-200 border-t dark:border-gray-700 justify-between">
          <div className="flex justify-between items-center pt-5">
            {/* <!-- Button --> */}
            <button
              id="dropdownDefaultButton"
              data-dropdown-toggle="lastDaysdropdown"
              data-dropdown-placement="bottom"
              className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-gray-900 text-center inline-flex items-center dark:hover:text-white"
              type="button"
            >
              Last 7 days
              <svg
                className="w-2.5 m-2.5 ms-1.5"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 10 6"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="m1 1 4 4 4-4"
                />
              </svg>
            </button>
            {/* <!-- Dropdown menu --> */}
            <div
              id="lastDaysdropdown"
              className="z-10 hidden bg-white divide-y divide-gray-100 rounded-lg shadow w-44 dark:bg-gray-700"
            >
              <ul
                className="py-2 text-sm text-gray-700 dark:text-gray-200"
                aria-labelledby="dropdownDefaultButton"
              >
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
                  >
                    Yesterday
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
                  >
                    Today
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
                  >
                    Last 7 days
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
                  >
                    Last 30 days
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
                  >
                    Last 90 days
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
