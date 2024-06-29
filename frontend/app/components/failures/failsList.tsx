import FailsRow from "./failsRow";

type Props = {
  failures: Failure[];
};

type Failure = {
  searchId: number;
  location: string;
  distanceRadius: number;
  date: string;
  status: number;
  url: string;
};

export default function FailsList({ failures }: Props) {
  const sortedFailures = failures.sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
  );
  return (
    <>
      <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800 xl:max-h-[65vh] xl:overflow-y-auto">
        <div className="items-center justify-between flex">
          <div className="mb-4 lg:mb-0">
            <h3 className="mb-2 text-xl font-bold text-gray-900 dark:text-white">
              Most recent failures
            </h3>
            <span className="text-base font-normal text-gray-500 dark:text-gray-400">
              This is a list of the most recent scan failures
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
                        ID
                      </th>
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
                        Status Code
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Date
                      </th>
                      <th
                        scope="col"
                        className="p-4 text-xs font-medium tracking-wider text-left text-gray-500 uppercase dark:text-white"
                      >
                        Scan
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800">
                    {sortedFailures.map((failure, id) => {
                      return (
                        <FailsRow
                          index={id}
                          failure={failure}
                          key={id}
                        ></FailsRow>
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
