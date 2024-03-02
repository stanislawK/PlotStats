"use client";

import Link from "next/link";

import { useFormState } from "react-dom";

type Props = {
  registerUserFunc: any;
  hasFreshToken: boolean;
  response?: string;
};

export default function RegisterUser({
  registerUserFunc,
  hasFreshToken,
  response,
}: Props) {
  async function registerNewUser(
    previousState: string | undefined | null,
    formData: FormData
  ) {
    const email = formData.get("email");
    const response = await registerUserFunc(email);
    const form = document.getElementById("registerUserForm") as HTMLFormElement;
    form.reset();
    return response;
  }
  const [state, formAction] = useFormState(registerNewUser, "");
  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          Register new user:
        </h3>
      </div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white my-4">
        {state}
      </h3>
      {!hasFreshToken && (
        <div className="inline-flex">
          <p className="text-lg text-gray-900 dark:text-white">Please&nbsp;</p>
          <Link
            href="/logout"
            className="text-lg font-semibold text-blue-600 dark:text-blue-500 hover:underline"
          >
            log out
          </Link>
          <p className="text-lg text-gray-900 dark:text-white">
            &nbsp;and login again.
          </p>
        </div>
      )}
      {!!response && response != "" && (
        <p className="text-lg font-semibold text-gray-900 dark:text-white">
          {response}
        </p>
      )}
      {!!hasFreshToken && (
        <form id="registerUserForm" action={formAction}>
          <div className="relative mb-7">
            <input
              type="text"
              id="email"
              name="email"
              className="block px-2.5 pb-2.5 pt-4 w-full text-sm text-gray-900 bg-transparent rounded-lg border-1 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer"
              placeholder=" "
              required
            />
            <label
              htmlFor="email"
              className="absolute text-sm text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-4 scale-75 top-2 z-10 origin-[0] bg-white dark:bg-gray-900 px-2 peer-focus:px-2 peer-focus:text-blue-600 peer-focus:dark:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:-translate-y-1/2 peer-placeholder-shown:top-1/2 peer-focus:top-2 peer-focus:scale-75 peer-focus:-translate-y-4 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto start-1"
            >
              User Email
            </label>
          </div>

          <button
            type="submit"
            className="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
          >
            Add new user
          </button>
        </form>
      )}
    </div>
  );
}
