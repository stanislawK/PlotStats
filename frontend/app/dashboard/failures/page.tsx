import { getCookie } from "cookies-next";
import { cookies } from "next/headers";
import { getAllSearches, getFailRate } from "../../utils/searchStats";
import FailRateChart from "@/app/components/failures/failRate";

type Props = {
  searchParams: Record<string, string> | null | undefined;
};

export default async function Failures({ searchParams }: Props) {
  const accessToken = getCookie("accessToken", { cookies });
  const allSearches = await getAllSearches(accessToken);
  const failRate = await getFailRate(30, accessToken);

  return (
    <>
      <div className="p-4 sm:ml-64">
        <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
          <div className="grid w-full grid-cols-1 gap-4 mt-4 xl:grid-cols-2 mb-4">
            <FailRateChart
              failures={failRate.failures}
              successes={failRate.successes}
            ></FailRateChart>
          </div>
          <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800"></div>
        </div>
      </div>
    </>
  );
}
