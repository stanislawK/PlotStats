"use client";

import dynamic from "next/dynamic";
import PriceChange from "./priceChange";
const ApexChart = dynamic(() => import("react-apexcharts"), { ssr: false });

type Props = {
  failures: Failure[];
  successes: {
    searchId: number
    successes: string[]
  }[]
};

type Failure = {
  searchId: number;
  failures: {
    date: string
    status: number
  }[]
};


export default function SuccessRateChart({ failures, successes }: Props) {
  const getSuccessDates = successes.flatMap(item => item.successes)
              .map(dateTime => dateTime.split('T')[0])
  const getFailureDates = failures
      .flatMap((item) => item.failures.map((failure) => failure.date))
      .map((dateTime) => dateTime.split("T")[0])
  const allDates = [...getSuccessDates, ...getFailureDates]
  const uniqueDatesSet = new Set<string>(allDates);
  const uniqueDatesArray: string[] = Array.from(uniqueDatesSet);
  const countsPerDate: { [key: string]: { successes: number; failures: number } } = {};
  uniqueDatesSet.forEach(date => {
    countsPerDate[date] = { successes: 0, failures: 0 };
  });
  // Count successes per date
successes.forEach(item => {
  item.successes.forEach(dateTime => {
    const date = dateTime.split('T')[0];
    countsPerDate[date].successes++;
  });
});
// Count failures per date
failures.forEach(item => {
  item.failures.forEach(failure => {
    const date = failure.date.split('T')[0];
    countsPerDate[date].failures++;
  });
});

console.log(countsPerDate);
  console.log(getDates)
  console.log(uniqueDatesArray)
  const allSeries = {
    uniqueDatesArray: uniqueDatesArray,
    minPrices: Array.from(
      events,
      (event) => event.minPricePerSquareMeter.pricePerSquareMeter
    ),
    avgPrice: allAvgPrices,
  };
  const avgArea = events[events.length - 1]?.avgAreaInSquareMeters;
  const mainChartColors = {
    borderColor: "#F3F4F6",
    labelColor: "#6B7280",
    opacityFrom: 0.45,
    opacityTo: 0,
  };
  const series = [
    {
      name: "Succeeded scans",
      data: allSeries.avgPrice,
      color: "#32a852",
    },
    {
      name: "Failed scans",
      data: allSeries.minPrices,
      color: "#a8323a",
    },
  ];
  const option = {
    fill: {
      type: "gradient",
      gradient: {
        enabled: true,
        opacityFrom: mainChartColors.opacityFrom,
        opacityTo: mainChartColors.opacityTo,
      },
    },
    dataLabels: {
      enabled: false,
    },
    tooltip: {
      style: {
        fontSize: "14px",
        fontFamily: "Inter, sans-serif",
      },
    },
    grid: {
      show: true,
      borderColor: mainChartColors.borderColor,
      strokeDashArray: 1,
      padding: {
        left: 35,
        bottom: 15,
      },
    },
    markers: {
      size: 5,
      strokeColors: "#ffffff",
      hover: {
        size: undefined,
        sizeOffset: 3,
      },
    },
    xaxis: {
      categories: allSeries.dates,
      labels: {
        style: {
          colors: [mainChartColors.labelColor],
          fontSize: "14px",
          fontWeight: 500,
        },
      },
      axisBorder: {
        color: mainChartColors.borderColor,
      },
      axisTicks: {
        color: mainChartColors.borderColor,
      },
      crosshairs: {
        show: true,
        position: "back",
        stroke: {
          color: mainChartColors.borderColor,
          width: 1,
          dashArray: 10,
        },
      },
    },
    yaxis: {
      labels: {
        style: {
          colors: [mainChartColors.labelColor],
          fontSize: "14px",
          fontWeight: 500,
        },
        formatter: function (value) {
          return "PLN" + value;
        },
      },
    },
    legend: {
      fontSize: "14px",
      fontWeight: 500,
      fontFamily: "Inter, sans-serif",
      labels: {
        colors: [mainChartColors.labelColor],
      },
      itemMargin: {
        horizontal: 10,
      },
    },
    responsive: [
      {
        breakpoint: 1024,
        options: {
          xaxis: {
            labels: {
              show: false,
            },
          },
        },
      },
    ],
  };

  return (
    <>
      <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm w-full dark:border-gray-700 sm:p-6 dark:bg-gray-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex-shrink-0">
            <span className="text-xl font-bold leading-none text-gray-900 sm:text-2xl dark:text-white">
              {avgArea} sq meters
            </span>
            <h3 className="text-base font-light text-gray-500 dark:text-gray-400">
              Avg area this week
            </h3>
          </div>
          <PriceChange allAvgPrices={allAvgPrices}></PriceChange>
        </div>
        <div id="main-chart">
          <ApexChart
            options={option}
            series={series}
            height={420}
            width="100%"
            type="area"
          />
        </div>
        {/* <!-- Card Footer --> */}
        <div className="flex items-center justify-between pt-3 mt-4 border-t border-gray-200 sm:pt-6 dark:border-gray-700">
          <div>
            <button
              className="inline-flex items-center p-2 text-sm font-medium text-center text-gray-500 rounded-lg hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              type="button"
              data-dropdown-toggle="weekly-sales-dropdown"
            >
              Last 7 days{" "}
              <svg
                className="w-4 h-4 ml-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 9l-7 7-7-7"
                ></path>
              </svg>
            </button>
            {/* <!-- Dropdown menu --> */}
            <div
              className="z-50 hidden my-4 text-base list-none bg-white divide-y divide-gray-100 rounded shadow dark:bg-gray-700 dark:divide-gray-600"
              id="weekly-sales-dropdown"
            >
              <div className="px-4 py-3" role="none">
                <p
                  className="text-sm font-medium text-gray-900 truncate dark:text-white"
                  role="none"
                >
                  Sep 16, 2021 - Sep 22, 2021
                </p>
              </div>
              <ul className="py-1" role="none">
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-600 dark:hover:text-white"
                    role="menuitem"
                  >
                    Yesterday
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-600 dark:hover:text-white"
                    role="menuitem"
                  >
                    Today
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-600 dark:hover:text-white"
                    role="menuitem"
                  >
                    Last 7 days
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-600 dark:hover:text-white"
                    role="menuitem"
                  >
                    Last 30 days
                  </a>
                </li>
                <li>
                  <a
                    href="#"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-600 dark:hover:text-white"
                    role="menuitem"
                  >
                    Last 90 days
                  </a>
                </li>
              </ul>
              <div className="py-1" role="none">
                <a
                  href="#"
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-600 dark:hover:text-white"
                  role="menuitem"
                >
                  Custom...
                </a>
              </div>
            </div>
          </div>
          <div className="flex-shrink-0">
            <a
              href="#"
              className="inline-flex items-center p-2 text-xs font-medium uppercase rounded-lg text-primary-700 sm:text-sm hover:bg-gray-100 dark:text-primary-500 dark:hover:bg-gray-700"
            >
              Sales Report
              <svg
                className="w-4 h-4 ml-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 5l7 7-7 7"
                ></path>
              </svg>
            </a>
          </div>
        </div>
      </div>
    </>
  );
}
