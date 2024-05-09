import NewSearch from "../../components/searches/newSearch";
import SearchesLists from "../../components/searches/searches";
import {
  adhocScan,
  addFavorite,
  addToUsers,
  onDemandScan,
} from "../../utils/scan";
import { getCookie } from "cookies-next";
import { cookies } from "next/headers";
import { revalidatePath } from "next/cache";
import {
  getUserSearches,
  getAllSearches,
  getLastStatuses,
} from "../../utils/searchStats";
import { redirect } from "next/navigation";
import { isAdminUser } from "@/app/utils/users";

type ScanData = {
  day: number;
  hour: number;
  minute: number;
  url: string;
};

type Props = {
  searchParams: Record<string, string> | null | undefined;
};

export default async function Searches({ searchParams }: Props) {
  const addFavoriteId = searchParams?.favorite;
  const newUsersSearchId = searchParams?.users;
  const onDemandSearchId = searchParams?.ondemand;

  // @ts-ignore
  const accessToken: string = getCookie("accessToken", { cookies });
  if (addFavoriteId !== undefined && !isNaN(parseInt(addFavoriteId))) {
    ("use server");
    await addFavorite(addFavoriteId, accessToken);
    revalidatePath("/dashboard/searches");
  }
  if (newUsersSearchId !== undefined && !isNaN(parseInt(newUsersSearchId))) {
    ("use server");
    await addToUsers(newUsersSearchId, accessToken);
    revalidatePath("/dashboard/searches");
  }
  const userSearches = await getUserSearches(accessToken, true);
  const allSearches = await getAllSearches(accessToken);
  const lastStatuses = await getLastStatuses(accessToken);
  if (onDemandSearchId !== undefined && !isNaN(parseInt(onDemandSearchId))) {
    ("use server");
    const toFetch = userSearches.searches.find(
      // @ts-ignore
      (search) => search.id == onDemandSearchId
    );
    if (!!toFetch?.url) {
      await onDemandScan(toFetch.url, accessToken);
      redirect("/dashboard/searches");
    }
  }
  const adhocScanFunc = async (data: ScanData) => {
    "use server";
    await adhocScan(data, accessToken);
    revalidatePath("/dashboard/searches");
  };
  const isAdmin = await isAdminUser(accessToken);
  return (
    <div className="p-4 sm:ml-64">
      <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
        <SearchesLists
          userSearches={userSearches.searches}
          allSearches={allSearches.searches}
          favSearchId={userSearches?.favoriteId}
          isAdmin={isAdmin}
          statuses={lastStatuses.statuses} 
        ></SearchesLists>
        <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800">
          <NewSearch adhocScanFunc={adhocScanFunc}></NewSearch>
        </div>
      </div>
    </div>
  );
}
