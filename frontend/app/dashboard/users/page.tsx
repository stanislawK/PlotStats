import { cookies } from "next/headers";
import { getCookie } from "cookies-next";
import UsersList from "@/app/components/users/usersList";
import { getUsers } from "@/app/utils/users";

export default async function Users() {
  const accessToken = getCookie("accessToken", { cookies });
  const users = await getUsers(accessToken);

  return (
    <>
      <div className="p-4 sm:ml-64">
        <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
          <div className="grid w-full grid-cols-1 gap-4 mt-4 xl:grid-cols-2 mb-4">
            <UsersList users={users}></UsersList>
          </div>
        </div>
      </div>
    </>
  );
}
