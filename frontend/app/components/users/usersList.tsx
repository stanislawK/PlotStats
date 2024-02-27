import Link from "next/link";

type User = {
  id: number;
  email: string;
  roles: string[];
  isActive: boolean;
};

type Props = {
  users: User[];
};

export default async function UsersList({ users }: Props) {
  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          All Users:
        </h3>
      </div>
      <ul role="list" className="divide-y divide-gray-200 dark:divide-gray-700">
        {users.map((user) => {
          return (
            <li
              className={`py-3 sm:py-4 hover:bg-gray-50 hover:pl-2 hover:transition-all`}
              key={user.id}
            >
              <div className={`flex items-center space-x-4`}>
                <div className="flex-shrink-0">{user.id}.</div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 truncate dark:text-white">
                    {user.email}
                  </p>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-gray-900 truncate dark:text-white">
                    {user.roles}
                  </p>
                </div>
                <div className="flex-1 inline-flex">
                  Active:
                  {user.isActive ? (
                    <svg
                      className="w-6 h-6 text-green-400 dark:text-white ml-2"
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
                        d="m5 12 4.7 4.5 9.3-9"
                      />
                    </svg>
                  ) : (
                    <svg
                      className="w-6 h-6 text-red-600 dark:text-white"
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
                        d="M6 18 18 6m0 12L6 6"
                      />
                    </svg>
                  )}
                </div>
                <div className="inline-flex items-center text-base font-semibold text-gray-900 dark:text-white">
                  {!!user.isActive && !user.roles.includes("admin") && (
                    <>
                      <span className="group relative z-100">
                        <div
                          className={`absolute bottom-[calc(100%+0.4rem)] left-[50%] -translate-x-[75%] hidden group-hover:block w-auto`}
                        >
                          <div className="bottom-full right-0 rounded bg-black px-3 py-1 text-xs text-white whitespace-nowrap">
                            Deactivate
                          </div>
                        </div>
                        <Link href="">
                          <svg
                            className="w-6 h-6 text-gray-800 dark:text-white hover:text-red-600"
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
                              d="M12 14v3m-3-6V7a3 3 0 1 1 6 0v4m-8 0h10c.6 0 1 .4 1 1v7c0 .6-.4 1-1 1H7a1 1 0 0 1-1-1v-7c0-.6.4-1 1-1Z"
                            />
                          </svg>
                        </Link>
                      </span>
                    </>
                  )}
                  {!user.isActive && (
                    <>
                      <span className="group relative z-100">
                        <div className="absolute bottom-[calc(100%+0.4rem)] left-[50%] -translate-x-[75%] hidden group-hover:block w-auto">
                          <div className="bottom-full right-0 rounded bg-black px-3 py-1 text-xs text-white whitespace-nowrap">
                            Activate
                          </div>
                        </div>
                        <Link href="">
                          <svg
                            className="w-6 h-6 text-gray-800 dark:text-white hover:text-green-500"
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
                              d="M10 14v3m4-6V7a3 3 0 1 1 6 0v4M5 11h10c.6 0 1 .4 1 1v7c0 .6-.4 1-1 1H5a1 1 0 0 1-1-1v-7c0-.6.4-1 1-1Z"
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
        })}
      </ul>
    </div>
  );
}
