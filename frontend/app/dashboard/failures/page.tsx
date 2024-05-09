import { getCookie } from "cookies-next";
import { cookies } from "next/headers";
import { getAllSearches, getFailRate } from "../../utils/searchStats";
import FailRateChart from "@/app/components/failures/failRate";
import FailsList from "@/app/components/failures/failsList";
import { onDemandScan } from "@/app/utils/scan";
import { redirect } from "next/navigation";
import RatePerSearchChart from "@/app/components/failures/ratePerSearch";

type Props = {
  searchParams: Record<string, string> | null | undefined;
};

type Failures = {
  searchId: number;
  failures: {
    date: string;
    status: number;
  }[];
}[];

type RecentFailure = {
  searchId: number;
  location: string;
  distanceRadius: number;
  date: string;
  status: number;
};

type Searches = {
  category: {
    name: string;
  };
  distanceRadius: number;
  fromPrice?: number;
  fromSurface?: number;
  id: number;
  location: string;
  toPrice?: number;
  toSurface?: number;
  url: string;
}[];

type ReducedSearch = {
  id: number;
  location: string;
};

function getRecentFailures(
  searches: Searches,
  failures: Failures
): RecentFailure[] {
  const recentFailures: RecentFailure[] = [];
  failures.forEach((failure) => {
    const search = searches.find((search) => search.id == failure.searchId);
    failure.failures.forEach((singleFail) => {
      // @ts-ignore
      const recentFailure: RecentFailure = {};
      // @ts-ignore
      recentFailure.searchId = search.id;
      // @ts-ignore
      recentFailure.location = search.location;
      // @ts-ignore
      recentFailure.distanceRadius = search.distanceRadius;
      recentFailure.date = singleFail.date;
      recentFailure.status = singleFail.status;
      recentFailures.push(recentFailure);
    });
  });
  const sorted = recentFailures.sort((a, b) => a.date.localeCompare(b.date));
  return sorted;
}

export default async function Failures({ searchParams }: Props) {
  const onDemandSearchId = searchParams?.ondemand;
  const accessToken = getCookie("accessToken", { cookies });
  // @ts-ignore
  const allSearches = await getAllSearches(accessToken);
  // @ts-ignore
  const failRate = await getFailRate(30, accessToken);
  const recentFailures = getRecentFailures(
    allSearches.searches,
    failRate.failures
  );
  const reducedSearches: ReducedSearch[] = allSearches.searches
    .map(
      // @ts-ignore
      (search): ReducedSearch => ({
        id: search.id,
        location: search.location,
      })
    )
    .sort(
      // @ts-ignore
      (a, b) => a.id - b.id
    );

  if (onDemandSearchId !== undefined && !isNaN(parseInt(onDemandSearchId))) {
    ("use server");
    const toFetch = allSearches.searches.find(
      // @ts-ignore
      (search) => search.id == onDemandSearchId
    );
    if (!!toFetch?.url) {
      // @ts-ignore
      await onDemandScan(toFetch.url, accessToken);
      redirect("/dashboard/failures");
    }
  }

  return (
    <>
      <div className="p-4 sm:ml-64">
        <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
          <div className="grid w-full grid-cols-1 gap-4 mt-4 xl:grid-cols-2 mb-4">
            <FailRateChart
              failures={failRate.failures}
              successes={failRate.successes}
            ></FailRateChart>
            <FailsList failures={recentFailures.slice(0, 15)}></FailsList>
          </div>
          <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800">
            <RatePerSearchChart
              failures={failRate.failures}
              successes={failRate.successes}
              searches={reducedSearches}
            ></RatePerSearchChart>
          </div>
        </div>
      </div>
    </>
  );
}
