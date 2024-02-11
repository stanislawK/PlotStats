import UserSearch from "./userSearch";

type Props = {
  userSearches: {
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
    url: string;
  }[];
  allSearches: {
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
    url: string;
  }[];
  favSearchId?: number;
};

export default async function SearchesLists({
  userSearches,
  allSearches,
  favSearchId,
}: Props) {
  const userSearchesIds = Array.from(userSearches, (search) => search.id);
  return (
    <>
      <div className="grid w-full grid-cols-1 gap-4 mt-4 xl:grid-cols-2 mb-4">
        {/* Users searches */}
        <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800 xl:max-h-[65vh] xl:overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Your searches
            </h3>
          </div>
          <ul
            role="list"
            className="divide-y divide-gray-200 dark:divide-gray-700"
          >
            {userSearches.map((search) => {
              return (
                <UserSearch
                  search={search}
                  key={search.id}
                  favSearchId={favSearchId}
                ></UserSearch>
              );
            })}
          </ul>
        </div>
        {/* All other searches */}
        <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800 xl:max-h-[65vh] xl:overflow-y-auto">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Other searches
            </h3>
          </div>
          <ul
            role="list"
            className="divide-y divide-gray-200 dark:divide-gray-700"
          >
            {allSearches.map((search) => {
              if (userSearchesIds && userSearchesIds.includes(search.id)) {
                return;
              }
              return <UserSearch search={search} key={search.id}></UserSearch>;
            })}
          </ul>
        </div>
      </div>
    </>
  );
}
