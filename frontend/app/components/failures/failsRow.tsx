import RunScanBtn from "./runScanBtn";
import { onDemandScan } from "@/app/utils/scan";
import { cookies } from "next/headers";
import { getCookie } from "cookies-next";
import { redirect } from "next/navigation";

type Props = {
  failure: Failure;
  index: number;
};

type Failure = {
  searchId: number;
  location: string;
  distanceRadius: number;
  date: string;
  status: number;
  url: string;
};

export default function FailsRow({ failure, index }: Props) {
  // @ts-ignore
  const accessToken: string = getCookie("accessToken", { cookies });
  const isEven = index % 2 === 0;
  return (
    <tr
      className={
        isEven
          ? "bg-gray-50 dark:bg-gray-700 hover:bg-white"
          : "hover:bg-gray-50 dark:hover:bg-gray-600"
      }
    >
      <td className="p-4 text-sm font-normal text-gray-900 whitespace-nowrap dark:text-white">
        {failure.searchId}
      </td>
      <td className="p-4 text-sm font-normal text-gray-900 whitespace-nowrap dark:text-white">
        {failure.location}
        {"; "}
        <span className="font-semibold">{failure.distanceRadius} km</span>
      </td>
      <td className="p-4 text-sm text-gray-500 whitespace-nowrap dark:text-white">
        {failure.status}
      </td>
      <td className="inline-flex items-center p-4 space-x-2 text-sm text-gray-900 whitespace-nowrap dark:text-gray-400 font-semibold">
        {failure.date.split("T")[0]}
      </td>
      <td className="p-4 whitespace-nowrap">
        <form
          action={async (formData) => {
            "use server";
            await onDemandScan(failure.url, accessToken);
            redirect("failures");
          }}
        >
          <RunScanBtn></RunScanBtn>
        </form>
      </td>
    </tr>
  );
}
