"use client";

import { Dialog, Transition } from "@headlessui/react";
import { Fragment, useState } from "react";
import { useRouter } from "next/navigation";
import { FormEvent } from "react";
import Link from "next/link";

type Props = {
  activateAccountFunc: any;
};
export default async function ActivateAccountModal({
  activateAccountFunc,
}: Props) {
  let [isOpen, setIsOpen] = useState(true);
  const router = useRouter();
  function closeModal() {
    setIsOpen(false);
    router.push("/");
  }

  function activateAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const email = formData.get("email");
    const tempPassword = formData.get("tempPassword");
    const newPassword = formData.get("newPassword");
    activateAccountFunc({
      tempPassword: tempPassword,
      email: email,
      newPassword: newPassword,
    });
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
                    Activate your account
                  </Dialog.Title>
                  <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
                    <form className="space-y-6" onSubmit={activateAccount}>
                      <div>
                        <label
                          htmlFor="email"
                          className="block text-sm font-medium leading-6 text-gray-900"
                        >
                          Email address
                        </label>
                        <div className="mt-2">
                          <input
                            id="email"
                            name="email"
                            type="email"
                            autoComplete="email"
                            required
                            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-cyan-400 sm:text-sm sm:leading-6"
                          />
                        </div>
                      </div>

                      <div>
                        <div className="flex items-center justify-between">
                          <label
                            htmlFor="tempPassword"
                            className="block text-sm font-medium leading-6 text-gray-900"
                          >
                            Temporary Password
                          </label>
                        </div>
                        <div className="mt-2">
                          <input
                            id="tempPassword"
                            name="tempPassword"
                            type="password"
                            autoComplete="current-tempPassword"
                            required
                            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-cyan-400 sm:text-sm sm:leading-6"
                          />
                        </div>
                      </div>
                      <div>
                        <div className="flex items-center justify-between">
                          <label
                            htmlFor="newPassword"
                            className="block text-sm font-medium leading-6 text-gray-900"
                          >
                            New Password
                          </label>
                        </div>
                        <div className="mt-2">
                          <input
                            id="newPassword"
                            name="newPassword"
                            type="password"
                            autoComplete="current-newPassword"
                            required
                            className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-cyan-400 sm:text-sm sm:leading-6"
                          />
                          <p
                            id="helper-text-explanation"
                            className="mt-2 text-sm text-gray-500 dark:text-gray-400"
                          >
                            Password must contain at least one uppercase letter,
                            one lowercase letter, one digit, and one special
                            character{" "}
                          </p>
                        </div>
                      </div>

                      <div>
                        <button
                          type="submit"
                          className="flex w-full justify-center rounded-md bg-cyan-500 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-cyan-400 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-500"
                        >
                          Activate Account
                        </button>
                      </div>
                    </form>

                    <p className="mt-10 text-center text-sm text-gray-500">
                      Have toy had activated your account already?{" "}
                      <Link
                        href="/?loginModal=true"
                        className="font-semibold leading-6 text-cyan-500 hover:text-cyan-300"
                      >
                        Login
                      </Link>
                    </p>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </>
  );
}
