"use client";

type Props = {
  allStats: {
    avgAreaTotal: number;
    avgTerrainTotal?: number;
    avgPricePerSquareMeterTotal: number;
    avgPriceTotal: number;
    category: {
      name: string;
    };
    dateFrom: string;
    dateTo: string;
    distanceRadius: number;
    fromPrice?: number;
    fromSurface?: number;
    location: string;
    toPrice?: number;
    toSurface?: number;
  };
};

export default async function SearchSummary({ allStats }: Props) {
  console.log(allStats);
  return (
    <>
      <div className="grid w-full grid-cols-1 gap-4 mt-4 xl:grid-cols-2 2xl:grid-cols-3 mb-4">
        {/* Search main info */}
        <div className="items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm sm:flex dark:border-gray-700 sm:p-6 dark:bg-gray-800">
          <div className="w-full">
            <h3 className="text-base font-normal text-gray-500 dark:text-gray-400">
              Category: {allStats.category.name}
            </h3>
            <span className="text-xl font-bold leading-none text-gray-900 sm:text-2xl dark:text-white">
              {allStats.location} +/- {allStats.distanceRadius}km
            </span>
            <ul className="pl-4 my-4 space-y-3 text-gray-500 list-disc dark:text-gray-400">
              <li>
                Price range: {allStats.fromPrice || "N/A"} -{" "}
                {allStats.toPrice || "N/A"}
              </li>
              <li>
                Size range: {allStats.fromSurface || "N/A"} sq m -{" "}
                {allStats.toSurface || "N/A"} sq m
              </li>
              <li>
                Date range: {allStats.dateFrom.substring(0, 10)} -{" "}
                {allStats.dateFrom.substring(0, 10)}
              </li>
            </ul>
          </div>
        </div>
        {/* Total stats */}
        <div className="items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm sm:flex dark:border-gray-700 sm:p-6 dark:bg-gray-800">
          <div className="p-1">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Total search statistics
              </h3>
            </div>
            <ol className="relative border-l border-gray-200 dark:border-gray-700">
              <li className="mb-10 ml-4">
                <div className="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -left-1.5 border border-white dark:border-gray-800 dark:bg-gray-700"></div>
                <time className="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">
                  Area
                </time>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {allStats.avgAreaTotal} square meters
                </h3>
                <p className="mb-4 text-base font-normal text-gray-500 dark:text-gray-400">
                  The average area across all events for that search.
                </p>
              </li>
              <li className="mb-10 ml-4">
                <div className="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -left-1.5 border border-white dark:border-gray-800 dark:bg-gray-700"></div>
                <time className="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">
                  Price per square meter
                </time>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {allStats.avgPricePerSquareMeterTotal} PLN
                </h3>
                <p className="mb-4 text-base font-normal text-gray-500 dark:text-gray-400">
                  The average price per square meter across all events.
                </p>
              </li>
              <li className="mb-4 ml-4">
                <div className="absolute w-3 h-3 bg-gray-200 rounded-full mt-1.5 -left-1.5 border border-white dark:border-gray-800 dark:bg-gray-700"></div>
                <time className="mb-1 text-sm font-normal leading-none text-gray-400 dark:text-gray-500">
                  Price
                </time>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {allStats.avgPriceTotal} PLN
                </h3>
                <p className="text-base font-normal text-gray-500 dark:text-gray-400">
                  The average estate price across all events in the selected
                  range.
                </p>
              </li>
            </ol>
          </div>
        </div>
        <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800">
          <div className="w-full">
            <h3 className="mb-2 text-base font-normal text-gray-500 dark:text-gray-400">
              Audience by age
            </h3>
            <div className="flex items-center mb-2">
              <div className="w-16 text-sm font-medium dark:text-white">
                50+
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                <div
                  className="bg-primary-600 h-2.5 rounded-full dark:bg-primary-500"
                  style={{ width: "18%" }}
                ></div>
              </div>
            </div>
            <div className="flex items-center mb-2">
              <div className="w-16 text-sm font-medium dark:text-white">
                40+
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                <div
                  className="bg-primary-600 h-2.5 rounded-full dark:bg-primary-500"
                  style={{ width: "15%" }}
                ></div>
              </div>
            </div>
            <div className="flex items-center mb-2">
              <div className="w-16 text-sm font-medium dark:text-white">
                30+
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                <div
                  className="bg-primary-600 h-2.5 rounded-full dark:bg-primary-500"
                  style={{ width: "60%" }}
                ></div>
              </div>
            </div>
            <div className="flex items-center mb-2">
              <div className="w-16 text-sm font-medium dark:text-white">
                20+
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                <div
                  className="bg-primary-600 h-2.5 rounded-full dark:bg-primary-500"
                  style={{ width: "30%" }}
                ></div>
              </div>
            </div>
          </div>
          <div id="traffic-channels-chart" className="w-full"></div>
        </div>
      </div>
    </>
  );
}
