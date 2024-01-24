import Image from "next/image";
import Link from "next/link";
import LoginModal from "./components/loginModal";
import { login } from "./utils/auth";
import { hasCookie } from "cookies-next";
import { cookies } from "next/headers";

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
      className="bg-cyan-400 px-10 py-5 text-2xl font-bold text-white hover:opacity-70 md:py-4 rounded-full"
    >
      {msg}
    </Link>
  );
}

export default function Home({ searchParams }: Props) {
  const showModal = searchParams?.loginModal;
  const hasToken = hasCookie("accessToken", { cookies });
  const loginFunc = async (data: LoginData) => {
    "use server";
    await login(data.email, data.password);
  };
  return (
    <main className="flex flex-col-reverse mb-10 mx-auto space-y-5 md:flex-row md:space-y-0 items-center md:mx-28 md:mt-10">
      {/* Content container */}
      <div className="flex flex-col mt-10 space-y-10 md:w-1/2 md:pl-10">
        <h1 className="text-center text-5xl font-bold md:text-left md:max-w-md">
          Unleash Data Insights
        </h1>
        <p className="text-center text-2xl text-gray-500 md:max-w-md md:text-left">
          Explore the dynamic world of real estate with our powerful dashboard.
          Instantly track and analyze price changes for apartments, plots, and
          houses. Your key to informed decisions in the ever-evolving property
          market.
        </p>
        <div className="mx-auto md:mx-0">
          <LinkBtn hasToken={hasToken}></LinkBtn>
        </div>
      </div>
      <div className="mx-auto mb-24 md:w-1/2">
        <Image
          src="/undraw_projections_re_ulc6.svg"
          alt="Dashboard Logo"
          width={1000}
          height={240}
          priority
        />
      </div>
      {/* Login modal */}
      {showModal && <LoginModal authenticate={loginFunc} />}
    </main>
  );
}
