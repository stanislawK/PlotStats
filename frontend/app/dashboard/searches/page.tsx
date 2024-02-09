import NewSearch from "../../components/searches/newSearch";
import SearchesLists from "../../components/searches/searches";
import { adhocScan } from "../../utils/scan";
import { getCookie } from "cookies-next";
import { cookies } from "next/headers";
import { revalidatePath } from "next/cache";
import { getUserSearches, getAllSearches } from "../../utils/searchStats";

type ScanData = {
  day: number;
  hour: number;
  minute: number;
  url: string;
};

export default async function Searches() {
  const accessToken = getCookie("accessToken", { cookies });
  const userSearches = await getUserSearches(accessToken, true);
  const allSearches = await getAllSearches(accessToken);
  const adhocScanFunc = async (data: ScanData) => {
    "use server";
    await adhocScan(data, accessToken);
    revalidatePath("/dashboard/searches");
  };
  return (
    <div className="p-4 sm:ml-64">
      <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
        <SearchesLists userSearches={userSearches.searches} allSearches={allSearches.searches} favSearchId={userSearches?.favoriteId}></SearchesLists>
        <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800">
          <NewSearch adhocScanFunc={adhocScanFunc}></NewSearch>
        </div>
      </div>
    </div>
  );
}
