import LogoutClient from "../components/logout/logout";
import { logout } from "../utils/auth";

export default async function Logout() {
  // We need to do it these way because deleting cookies works only on client components
  // but we canot use it in page.tsx in next 14
  const logoutFunc = async () => {
    "use server";
    await logout();
  };
  return (
    <>
      <LogoutClient logout={logoutFunc}></LogoutClient>
    </>
  );
}
