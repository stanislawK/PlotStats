import PriceRow from "./priceRow";
import type { Price } from "./priceRow";

type Props = {
  prices: Price[];
  type: string;
};

export default async function PriceList({ prices, type }: Props) {
  const isTotal = type === "total";
  return (
    <>
      <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm w-full dark:border-gray-700 sm:p-6 dark:bg-gray-800">
        <div className="items-center justify-between flex">
          <div className="mb-4 lg:mb-0">
            <h3 className="mb-2 text-xl font-bold text-gray-900 dark:text-white">
              {isTotal ? (
                "Lowest Prices"
              ) : (
                <>
                  Lowest per m<sup>2</sup>
                </>
              )}
            </h3>
            <span className="text-base font-normal text-gray-500 dark:text-gray-400">
              This is a list of the lowest prices{" "}
              {isTotal ? (
                ""
              ) : (
                <>
                  per m<sup>2</sup>
                </>
              )}{" "}
              from last search
            </span>
          </div>
        </div>
        <div className="flex flex-col mt-6">
          <div className="overflow-x-auto rounded-lg">
            <div className="inline-block min-w-full align-middle">
              <div className="overflow-hidden shadow sm:rounded-lg">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Title
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Price
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Area in square meters
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Price per m<sup>2</sup>
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Url
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800">
                    {prices.map((price, id) => {
                      return (
                        <PriceRow
                          price={price}
                          index={id}
                          key={id}
                          isTotal={isTotal}
                        ></PriceRow>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
