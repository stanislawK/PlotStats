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
  isAdmin: boolean;
};

export default async function SearchesLists({
  userSearches,
  allSearches,
  favSearchId,
  isAdmin,
}: Props) {
  let userSearchesIds: Array<number>;
  if (!!userSearches) {
    userSearchesIds = Array.from(userSearches, (search) => search.id);
  }
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
          {!userSearches && (
            <div
              id="alert-border-2"
              className="flex items-center p-4 mb-4 text-red-800 border-t-4 border-red-300 bg-red-50 dark:text-red-400 dark:bg-gray-800 dark:border-red-800"
              role="alert"
            >
              <svg
                className="flex-shrink-0 w-4 h-4"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z" />
              </svg>
              <div className="ms-3 text-sm font-medium">
                Select at least one search from the list of all searches.
              </div>
            </div>
          )}
          {!!userSearches && !favSearchId && (
            <div
              id="alert-border-2"
              className="flex items-center p-4 mb-4 text-red-800 border-t-4 border-red-300 bg-red-50 dark:text-red-400 dark:bg-gray-800 dark:border-red-800"
              role="alert"
            >
              <svg
                className="flex-shrink-0 w-4 h-4"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z" />
              </svg>
              <div className="ms-3 text-sm font-medium">
                Select your favorite search before going to the dashboard.
              </div>
            </div>
          )}
          <ul
            role="list"
            className="divide-y divide-gray-200 dark:divide-gray-700"
          >
            {userSearches &&
              userSearches.map((search) => {
                return (
                  <UserSearch
                    search={search}
                    key={search.id}
                    favSearchId={favSearchId}
                    isUsers={true}
                    isAdmin={isAdmin}
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
              return (
                <UserSearch
                  search={search}
                  key={search.id}
                  isUsers={false}
                ></UserSearch>
              );
            })}
          </ul>
        </div>
      </div>
    </>
  );
}
