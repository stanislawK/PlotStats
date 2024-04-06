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
import { getAllSearches, getFailRate } from "../../utils/searchStats";
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

export default async function Failures({ searchParams }: Props) {
  const accessToken = getCookie("accessToken", { cookies });
  const allSearches = await getAllSearches(accessToken);
  const failRate = await getFailRate(30, accessToken);
  console.log(JSON.stringify(failRate.failures, null, 4));
  const failures = [
    {
      searchId: 1,
      failures: [
        {
          date: "2024-03-31T18:37:44.797588",
          status: 403,
        },
      ],
    },
    {
      searchId: 2,
      failures: [
        {
          date: "2024-04-31T18:37:44.797588",
          status: 403,
        },
      ],
    },
  ];
  const uniqueDatesSet = new Set<string>(
    failures
      .flatMap((item) => item.failures.map((failure) => failure.date))
      .map((dateTime) => dateTime.split("T")[0])
  );
  console.log(uniqueDatesSet);

  return (
    <div className="p-4 sm:ml-64">
      <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
        <div className="grid w-full grid-cols-1 gap-4 mt-4 xl:grid-cols-2 mb-4"></div>
        <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800"></div>
      </div>
    </div>
  );
}
