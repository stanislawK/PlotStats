import { cookies } from "next/headers";
import { getCookie } from "cookies-next";

import SearchEventsStatsChart from "../components/dashboard/searchEventsStatsChart";
import SearchSummary from "../components/dashboard/searchDashboardSummary";
import PriceList from "../components/dashboard/priceList";
import {
  getSearchEventsStats,
  getSearchStats,
  getUserSearches,
  getLastEvent,
} from "../utils/searchStats";
import { redirect } from "next/navigation";

type Events = {
  id: number;
  avgAreaInSquareMeters: number;
  avgPrice: number;
  avgPricePerSquareMeter: number;
  avgTerrainAreaInSquareMeters?: number;
  date: string;
  minPrice: { price: number; pricePerSquareMeter: number };
  minPricePerSquareMeter: {
    areaInSquareMeters: number;
    price: number;
    pricePerSquareMeter: number;
  };
}[];

type Props = {
  searchParams: Record<string, string> | null | undefined;
};

export default async function Dashboard({ searchParams }: Props) {
  const accessToken = getCookie("accessToken", { cookies });
  const searchId = searchParams?.searchId;
  const searchEventsStats = await getSearchEventsStats(accessToken, searchId);
  if (
    searchEventsStats["searchEventsStats"]["__typename"] !=
    "SearchEventsStatsType"
  ) {
    redirect("/dashboard/searches");
  }
  const events: Events =
    searchEventsStats["searchEventsStats"]["searchEvents"] || [];
  const searchSummary = await getSearchStats(accessToken, searchId);
  const userSearches = await getUserSearches(accessToken);
  const lastEventId = Math.max(...Array.from(events, (event) => event.id));
  const lastEventPrices = await getLastEvent(lastEventId, accessToken);
  return (
    <div className="p-4 sm:ml-64">
      <div className="p-4 border-2 border-gray-200 border-dashed rounded-lg dark:border-gray-700">
        <SearchSummary
          allStats={searchSummary}
          searches={userSearches.searches}
        ></SearchSummary>
        <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800">
          <SearchEventsStatsChart events={events}></SearchEventsStatsChart>
        </div>
        <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800">
          <PriceList
            prices={lastEventPrices.minPrices}
            type={"total"}
          ></PriceList>
        </div>
        <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800">
          <PriceList
            prices={lastEventPrices.minPricesPerSquareMeter}
            type={"persqmeter"}
          ></PriceList>
        </div>
      </div>
    </div>
  );
}
