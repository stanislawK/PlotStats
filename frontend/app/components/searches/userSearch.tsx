import Link from "next/link";
import CategoryIcon from "../ui/categoryIcon";

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
    url: string;
  };
  favSearchId?: number;
  isUsers: boolean;
  isAdmin?: boolean;
};

export default function UserSearch({
  search,
  favSearchId,
  isUsers,
  isAdmin,
}: UserSearchProps) {
  return (
    <li className={`py-3 sm:py-4`}>
      <div className={`flex items-center space-x-4`}>
        <div className="flex-shrink-0">
          <CategoryIcon category={search.category.name}></CategoryIcon>
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 md:truncate dark:text-white text-wrap">
            {search.location}; {search.distanceRadius} km
          </p>
          <p className="text-sm text-gray-500 truncate dark:text-gray-400 2xl:inline 2xl:mr-3">
            <strong>Price:</strong> {search.fromPrice || "n/a"} PLN -{" "}
            {search.toPrice || "n/a"} PLN;
          </p>
          <p className="text-sm text-gray-500 truncate dark:text-gray-400 2xl:inline">
            <strong>Size:</strong> {search.fromSurface || "n/a"} sqm -{" "}
            {search.toSurface || "n/a"} sqm
          </p>

          <a
            href={search.url}
            className="flex items-center text-blue-600 hover:underline mt-1"
            rel="noopener noreferrer"
            target="_blank"
          >
            Go to original search
            <svg
              className="w-3 h-3 ms-2.5 rtl:rotate-[270deg]"
              aria-hidden="true"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 18 18"
            >
              <path
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M15 11v4.833A1.166 1.166 0 0 1 13.833 17H2.167A1.167 1.167 0 0 1 1 15.833V4.167A1.166 1.166 0 0 1 2.167 3h4.618m4.447-2H17v5.768M9.111 8.889l7.778-7.778"
              />
            </svg>
          </a>
        </div>
        <div className="inline-flex items-center text-base font-semibold text-gray-900 dark:text-white">
          {!!isUsers && !!isAdmin && (
            <>
              <span className="group relative z-100">
                <div
                  className={`absolute bottom-[calc(100%+0.4rem)] left-[50%] -translate-x-[75%] hidden group-hover:block w-auto`}
                >
                  <div className="bottom-full right-0 rounded bg-black px-3 py-1 text-xs text-white whitespace-nowrap">
                    On-demand run
                  </div>
                </div>
                <Link href={`searches/?ondemand=${search.id}`}>
                  <svg
                    className="w-[26px] h-[26px] text-gray-800 dark:text-white mr-2 mt-1 -rotate-45"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="1"
                      d="m10.051 8.102-3.778.322-1.994 1.994a.94.94 0 0 0 .533 1.6l2.698.316m8.39 1.617-.322 3.78-1.994 1.994a.94.94 0 0 1-1.595-.533l-.4-2.652m8.166-11.174a1.366 1.366 0 0 0-1.12-1.12c-1.616-.279-4.906-.623-6.38.853-1.671 1.672-5.211 8.015-6.31 10.023a.932.932 0 0 0 .162 1.111l.828.835.833.832a.932.932 0 0 0 1.111.163c2.008-1.102 8.35-4.642 10.021-6.312 1.475-1.478 1.133-4.77.855-6.385Zm-2.961 3.722a1.88 1.88 0 1 1-3.76 0 1.88 1.88 0 0 1 3.76 0Z"
                    />
                  </svg>
                </Link>
              </span>
            </>
          )}
          {!!isUsers && (
            <>
              <span className="group relative z-100">
                <div
                  className={`absolute bottom-[calc(100%+0.4rem)] left-[50%] -translate-x-[75%] hidden ${favSearchId == search.id ? "" : "group-hover:block"} w-auto`}
                >
                  <div className="bottom-full right-0 rounded bg-black px-3 py-1 text-xs text-white whitespace-nowrap">
                    Make your favorite
                  </div>
                </div>
                <Link href={`searches/?favorite=${search.id}`}>
                  <svg
                    className={`w-[26px] h-[26px] ${favSearchId && favSearchId == search.id ? "text-yellow-300 fill-current" : "text-gray-800 dark:text-white hover:text-yellow-300 hover:fill-current"}`}
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke="currentColor"
                      strokeWidth="0.9"
                      d="M11 5.1a1 1 0 0 1 2 0l1.7 4c.1.4.4.6.8.6l4.5.4a1 1 0 0 1 .5 1.7l-3.3 2.8a1 1 0 0 0-.3 1l1 4a1 1 0 0 1-1.5 1.2l-3.9-2.3a1 1 0 0 0-1 0l-4 2.3a1 1 0 0 1-1.4-1.1l1-4.1c.1-.4 0-.8-.3-1l-3.3-2.8a1 1 0 0 1 .5-1.7l4.5-.4c.4 0 .7-.2.8-.6l1.8-4Z"
                    />
                  </svg>
                </Link>
              </span>
            </>
          )}
          {!isUsers && (
            <>
              <span className="group relative z-100">
                <div className="absolute bottom-[calc(100%+0.4rem)] left-[50%] -translate-x-[75%] hidden group-hover:block w-auto">
                  <div className="bottom-full right-0 rounded bg-black px-3 py-1 text-xs text-white whitespace-nowrap">
                    Make it yours
                  </div>
                </div>
                <Link href={`searches/?users=${search.id}`}>
                  <svg
                    className="w-[30px] h-[30px] text-gray-800 dark:text-white rotate-180 hover:w-[40px] hover:hover:-translate-x-1 hover:transition hover:ease-in-out hover:text-green-500 2xl:mr-5"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="1.2"
                      d="M20 12H8m12 0-4 4m4-4-4-4M9 4H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h2"
                    />
                  </svg>
                </Link>
              </span>
            </>
          )}
        </div>
      </div>
    </li>
  );
}
