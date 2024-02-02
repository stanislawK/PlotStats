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
  searches: {
    category: {
      name: string;
    };
    distanceRadius: number;
    fromPrice?: number;
    fromSurface?: number;
    id: number;
    location: string;
    toPrice?: number;
    toSurface?: number;
  }[];
};

type CategoryProps = {
  category: string;
};

type UserSearchProps = {
  search: {
    category: {
      name: string;
    };
    distanceRadius: number;
    fromPrice?: number;
    fromSurface?: number;
    id: number;
    location: string;
    toPrice?: number;
    toSurface?: number;
  };
};

function CategoryIcon({ category }: CategoryProps) {
  if (category.toLowerCase() === "apartment") {
    return (
      <svg
        className="w-6 h-6 text-gray-800 dark:text-white"
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
          d="M6 4h12M6 4v16M6 4H5m13 0v16m0-16h1m-1 16H6m12 0h1M6 20H5M9 7h1v1H9V7Zm5 0h1v1h-1V7Zm-5 4h1v1H9v-1Zm5 0h1v1h-1v-1Zm-3 4h2a1 1 0 0 1 1 1v4h-4v-4a1 1 0 0 1 1-1Z"
        />
      </svg>
    );
  } else if (category.toLowerCase() === "house") {
    return (
      <svg
        className="w-6 h-6 text-gray-800 dark:text-white"
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
          d="m4 12 8-8 8 8M6 10.5V19c0 .6.4 1 1 1h3v-3c0-.6.4-1 1-1h2c.6 0 1 .4 1 1v3h3c.6 0 1-.4 1-1v-8.5"
        />
      </svg>
    );
  } else {
    return (
      <svg
        className="w-6 h-6 text-gray-800 dark:text-white"
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
          d="m3 16 5-7 6 6.5m6.5 2.5L16 13l-4.3 6m2.3-9h0M4 19h16c.6 0 1-.4 1-1V6c0-.6-.4-1-1-1H4a1 1 0 0 0-1 1v12c0 .6.4 1 1 1Z"
        />
      </svg>
    );
  }
}

function UserSearch({ search }: UserSearchProps) {
  return (
    <li className="py-3 sm:py-4">
      <div className="flex items-center space-x-4">
        <div className="flex-shrink-0">
          <CategoryIcon category={search.category.name}></CategoryIcon>
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 truncate dark:text-white">
            {search.location}
          </p>
          <p className="text-sm text-gray-500 truncate dark:text-gray-400 inline mr-3">
            <strong>Price:</strong> {search.fromPrice || "n/a"} PLN -{" "}
            {search.toPrice || "n/a"} PLN;
          </p>
          <p className="text-sm text-gray-500 truncate dark:text-gray-400 inline">
            <strong>Size:</strong> {search.fromSurface || "n/a"} sqm -{" "}
            {search.toSurface || "n/a"} sqm
          </p>
        </div>
        <div className="inline-flex items-center text-base font-semibold text-gray-900 dark:text-white">
          {search.distanceRadius} km
        </div>
      </div>
    </li>
  );
}

export default async function SearchSummary({ allStats, searches }: Props) {
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
                {allStats.dateTo.substring(0, 10)}
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
        {/* Users searches */}
        <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              All your searches
            </h3>
          </div>
          <ul
            role="list"
            className="divide-y divide-gray-200 dark:divide-gray-700"
          >
            {searches.map((search) => {
              return <UserSearch search={search} key={search.id}></UserSearch>;
            })}
          </ul>
        </div>
      </div>
    </>
  );
}
