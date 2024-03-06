import { cookies } from "next/headers";
import { getCookie } from "cookies-next";
import { getCategories, addCategory } from "@/app/utils/categories";
import CategoriesList from "@/app/components/categories/categoriesList";
import AddCategory from "@/app/components/categories/addCategory";
import { revalidatePath } from "next/cache";
import { isAdminUser } from "@/app/utils/users";

export default async function Categories() {
  const accessToken = getCookie("accessToken", { cookies });
  const categories = await getCategories(accessToken);
  const addCategoryFunc = async (name: string) => {
    "use server";
    await addCategory(name, accessToken);
    revalidatePath("/dashboard/schedules");
  };
  const isAdmin = await isAdminUser(accessToken);

  return (
    <>
      <div className="p-4 sm:ml-64">
        <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
          <div
            className={`grid w-full grid-cols-1 gap-4 mt-4 ${isAdmin ? "xl:grid-cols-2" : ""} mb-4`}
          >
            <CategoriesList categories={categories}></CategoriesList>
            {isAdmin && (
              <AddCategory addCategoryFunc={addCategoryFunc}></AddCategory>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
