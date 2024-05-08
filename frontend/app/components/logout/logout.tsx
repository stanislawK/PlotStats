"use client";
import { getCookie } from "cookies-next";
import { redirect } from "next/navigation";

type Props = {
  logout: any;
};

export default function LogoutClient({ logout }: Props) {
  const accessToken = getCookie("accessToken");
  const refreshToken = getCookie("refreshToken");
  if (!!accessToken || !!refreshToken) {
    logout();
  } else {
    redirect("/");
  }
  return <></>;
}
