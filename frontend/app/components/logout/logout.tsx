"use client";

type Props = {
  logout: any;
};

export default function LogoutClient({ logout }: Props) {
  logout();
  return <></>;
}
