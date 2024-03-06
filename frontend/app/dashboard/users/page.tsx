import { cookies } from "next/headers";
import { getCookie } from "cookies-next";
import UsersList from "@/app/components/users/usersList";
import type { User } from "@/app/components/users/usersList";
import RegisterUser from "@/app/components/users/registerUser";
import {
  getUsers,
  registerUsers,
  isTokenFresh,
  deactivateUser,
} from "@/app/utils/users";
import { revalidatePath } from "next/cache";
import DeactivateUserModal from "@/app/components/users/deactivateUserModal";

type Props = {
  searchParams: Record<string, string> | null | undefined;
};

export default async function Users({ searchParams }: Props) {
  const accessToken = getCookie("accessToken", { cookies });
  const isFreshToken = await isTokenFresh(accessToken);
  const users = await getUsers(accessToken);
  const userToDeactivateId = searchParams?.deactivateUser;
  let userToDeactivate: User | undefined = undefined;
  if (
    userToDeactivateId !== undefined &&
    !isNaN(parseInt(userToDeactivateId))
  ) {
    userToDeactivate = users.find(
      (user: User) => user.id == parseInt(userToDeactivateId)
    );
  }

  const registerUserFunc = async (email: string) => {
    "use server";
    const temp = await registerUsers(accessToken, email);
    revalidatePath("/dashboard/schedules");
    return temp;
  };
  const deactivateUserFunc = async (userId: number, email: string) => {
    "use server";
    if (userId == parseInt(userToDeactivateId)) {
      await deactivateUser(accessToken, email);
    }
    revalidatePath("/dashboard/users");
  };

  return (
    <>
      <div className="p-4 sm:ml-64">
        <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
          <div className="grid w-full grid-cols-1 gap-4 mt-4 xl:grid-cols-2 mb-4">
            <UsersList users={users}></UsersList>
            <RegisterUser
              hasFreshToken={isFreshToken}
              registerUserFunc={registerUserFunc}
            ></RegisterUser>
          </div>
        </div>
      </div>
      {!!userToDeactivate && (
        <DeactivateUserModal
          user={userToDeactivate}
          deactivateUserFunc={deactivateUserFunc}
          hasFreshToken={isFreshToken}
        ></DeactivateUserModal>
      )}
    </>
  );
}
