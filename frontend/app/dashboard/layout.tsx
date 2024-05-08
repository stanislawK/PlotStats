import Sidebar from "../components/sidebar";
import { getCookie } from "cookies-next";
import { cookies } from "next/headers";

export default function Layout({ children }: { children: React.ReactNode }) {
  const accessToken = getCookie("accessToken", { cookies });
  return (
    <>
      <Sidebar
        // @ts-ignore
        token={accessToken}
      ></Sidebar>
      {children}
    </>
  );
}
