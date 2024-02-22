import Link from "next/link";
import type { Search } from "./disabledList";

type DisabledRowProps = {
  search: Search;
  index: number;
};

export default function DisabledRow({ search, index }: DisabledRowProps) {
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
        {search.category.name}
      </td>
      <td className="p-4 text-sm font-semibold text-gray-900 whitespace-nowrap dark:text-white">
        {search.location}
      </td>
      <td className="p-4 text-sm font-normal text-gray-500 whitespace-nowrap dark:text-gray-400">
        {search.distanceRadius} km
      </td>
      <td className="p-4 whitespace-nowrap">
        <Link
          href={`/dashboard?searchId=${search.id}`}
          className="font-medium text-blue-600 dark:text-blue-500 hover:underline"
        >
          Check details
        </Link>
      </td>
      <td className="p-4 whitespace-nowrap">
        <Link
          href={`schedules?search=${search.id}`}
          className="font-medium text-blue-600 dark:text-blue-500 hover:underline"
        >
          Edit Schedule
        </Link>
      </td>
    </tr>
  );
}
