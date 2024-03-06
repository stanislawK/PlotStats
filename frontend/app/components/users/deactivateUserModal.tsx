"use client";

import { Dialog, Transition } from "@headlessui/react";
import { Fragment, useState } from "react";
import { useRouter } from "next/navigation";
import { FormEvent } from "react";
import Link from "next/link";

type Props = {
  deactivateUserFunc: any;
  hasFreshToken: boolean;
  user: {
    id: number;
    email: string;
    roles: string[];
    isActive: boolean;
  };
};

export default async function DeactivateUserModal({
  deactivateUserFunc,
  user,
  hasFreshToken,
}: Props) {
  let [isOpen, setIsOpen] = useState(true);
  const router = useRouter();
  function closeModal() {
    setIsOpen(false);
    router.push("/dashboard/users");
  }

  function deactivateUser(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    deactivateUserFunc(user.id, user.email);
    closeModal();
  }
  return (
    <>
      <Transition appear show={isOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={closeModal}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black/25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                  <button
                    className="absolute top-3 right-5 font-bold text-gray-500"
                    onClick={closeModal}
                  >
                    X
                  </button>
                  <Dialog.Title
                    as="h3"
                    className="mt-5 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900"
                  >
                    {!hasFreshToken ? (
                      <div className="inline-flex">
                        <p className="text-lg text-gray-900 dark:text-white">
                          Please&nbsp;
                        </p>
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
                    ) : (
                      <>Deactivate account: {user.email}</>
                    )}
                  </Dialog.Title>
                  {!!hasFreshToken && (
                    <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
                      <form className="space-y-6" onSubmit={deactivateUser}>
                        <div className="flex items-start mb-5">
                          <div className="flex items-center h-5">
                            <input
                              id="confirm"
                              type="checkbox"
                              value=""
                              className="w-4 h-4 border border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-blue-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800"
                              required
                            />
                          </div>
                          <label
                            htmlFor="confirm"
                            className="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300"
                          >
                            Confirmation of {user.email} account deactivation
                          </label>
                        </div>

                        <div>
                          <button
                            type="submit"
                            className="flex w-full justify-center rounded-md bg-cyan-500 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-cyan-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-500"
                          >
                            Deactivate
                          </button>
                        </div>
                      </form>

                      <p className="mt-10 text-center text-sm text-gray-500">
                        Please confirm that you want to deactivate account
                      </p>
                    </div>
                  )}
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </>
  );
}
