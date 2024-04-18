import Image from "next/image";
import Link from "next/link";
import LoginModal from "./components/loginModal";
import { login, activateAccount } from "./utils/auth";
import { hasCookie } from "cookies-next";
import { cookies } from "next/headers";
import ActivateAccountModal from "./components/users/activateModal";

type Props = {
  searchParams: Record<string, string> | null | undefined;
};

type TokenProps = {
  hasToken: boolean;
};

type LoginData = {
  email: string;
  password: string;
};

type ActivateAccountData = {
  email: string;
  tempPassword: string;
  newPassword: string;
};

function LinkBtn({ hasToken }: TokenProps) {
  let msg;
  let link;
  if (!!hasToken) {
    msg = "Dashboard";
    link = "/dashboard";
  } else {
    msg = "Get Started";
    link = "/?loginModal=true";
  }
  return (
    <Link
      href={link}
      className="inline-flex items-center justify-center px-5 py-3 text-base font-medium text-center text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-100 hover:border-cyan-400 focus:ring-4 focus:ring-gray-100 dark:text-white dark:border-gray-700 dark:hover:bg-gray-700 dark:focus:ring-gray-800"
    >
      {msg}
    </Link>
  );
}

export default function Home({ searchParams }: Props) {
  const showLoginModal = searchParams?.loginModal;
  const showActivateModal = searchParams?.activateModal;
  const hasToken = hasCookie("accessToken", { cookies });
  const loginFunc = async (data: LoginData) => {
    "use server";
    await login(data.email, data.password);
  };
  const activateUserFunc = async (data: ActivateAccountData) => {
    "use server";
    await activateAccount(data.email, data.tempPassword, data.newPassword);
  };
  return (
    <section className="bg-white dark:bg-gray-900">
      <div className="grid max-w-screen-xl h-screen px-4 py-8 mx-auto lg:gap-8 xl:gap-0 lg:py-16 lg:grid-cols-12">
        <div className="mr-auto place-self-center lg:col-span-7">
          <h1 className="max-w-2xl mb-4 text-4xl font-extrabold tracking-tight leading-none md:text-5xl xl:text-6xl dark:text-white">
            Unleash Data Insights
          </h1>
          <p className="max-w-2xl mb-6 font-light text-gray-500 lg:mb-8 md:text-lg lg:text-xl dark:text-gray-400">
            Explore the dynamic world of real estate with our powerful
            dashboard. Instantly track and analyze price changes for apartments,
            plots, and houses. Your key to informed decisions in the
            ever-evolving property market.
          </p>
          <LinkBtn hasToken={hasToken}></LinkBtn>
        </div>
        <div className="hidden lg:mt-0 lg:col-span-5 lg:flex">
          <Image
            src="/undraw_projections_re_ulc6.svg"
            alt="Dashboard Logo"
            width={1000}
            height={240}
            priority
          />
        </div>
      </div>
      {/* Login modal */}
      {showLoginModal && <LoginModal authenticate={loginFunc} />}
      {/* Activate Account Modal */}
      {showActivateModal && (
        <ActivateAccountModal
          activateAccountFunc={activateUserFunc}
        ></ActivateAccountModal>
      )}
    </section>
  );
}
