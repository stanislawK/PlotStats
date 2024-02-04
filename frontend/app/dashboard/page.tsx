import { cookies } from "next/headers";
import { getCookie } from "cookies-next";

import SearchEventsStatsChart from "../components/searchEventsStatsChart";
import SearchSummary from "../components/searchDashboardSummary";
import PriceList from "../components/priceList";
import {
  getFavSearchEventsStats,
  getSearchStats,
  getUserSearches,
  getLastEvent,
} from "../utils/searchStats";

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

export default async function Dashboard() {
  const accessToken = getCookie("accessToken", { cookies });
  const favSearchEventsStats = await getFavSearchEventsStats(accessToken);
  const events: Events =
    favSearchEventsStats["searchEventsStats"]["searchEvents"] || [];
  const searchSummary = await getSearchStats(accessToken);
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
          <PriceList prices={lastEventPrices.minPrices} type={"total"}></PriceList>
        </div>
        <div className="flex items-center justify-center mb-4 rounded bg-gray-50 dark:bg-gray-800">
          <PriceList prices={lastEventPrices.minPricesPerSquareMeter} type={"persqmeter"}></PriceList>
        </div>
      </div>
    </div>
  );
}
