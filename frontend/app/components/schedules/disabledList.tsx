import DisabledRow from "./disabledRow";

export type Search = {
  category: {
    name: string;
  };
  distanceRadius?: number;
  id: number;
  location: string;
  schedule?: {
    dayOfWeek: number;
    hour: number;
    minute: number;
  };
};

type Props = {
  searches: Search[];
};

export default async function DisabledList({ searches }: Props) {
  return (
    <>
      <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm w-full dark:border-gray-700 sm:p-6 dark:bg-gray-800">
        <div className="items-center justify-between flex">
          <div className="mb-4 lg:mb-0">
            <h3 className="mb-2 text-xl font-bold text-gray-900 dark:text-white">
              Searches with disabled schedule
            </h3>
            <span className="text-base font-normal text-gray-500 dark:text-gray-400">
              You can bring back search by editing its schedule
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
                        Category
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Location
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Radius
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Search Details
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Bring Back
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800">
                    {searches.map((search, id) => {
                      if (!search.schedule) {
                        return (
                          <DisabledRow
                            search={search}
                            key={id}
                            index={id}
                          ></DisabledRow>
                        );
                      }
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
