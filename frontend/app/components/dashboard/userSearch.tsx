import Link from "next/link";
import CategoryIcon from "../ui/categoryIcon";

type UserSearchProps = {
  search: {
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
  };
  currentSearchId: number;
};

export default function UserSearch({ search, currentSearchId }: UserSearchProps) {
  const isActive: boolean = search.id == currentSearchId;
  return (
    <li
      className={`py-3 sm:py-4 ${isActive ? "" : "hover:bg-gray-50 hover:pl-2 hover:transition-all"}`}
    >
      <Link href={"/dashboard/?searchId=" + search.id}>
        <div
          className={`flex items-center space-x-4 ${isActive ? "border-l-4 pl-2 border-green-500" : ""}`}
        >
          <div className="flex-shrink-0">
            <CategoryIcon category={search.category.name}></CategoryIcon>
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-medium text-gray-900 truncate dark:text-white">
              {search.location}
            </p>
            <p className="text-sm text-gray-500 truncate dark:text-gray-400 inline mr-3">
              <strong>Price:</strong> {search.fromPrice || "n/a"} PLN -{" "}
              {search.toPrice || "n/a"} PLN;
            </p>
            <p className="text-sm text-gray-500 truncate dark:text-gray-400 inline">
              <strong>Size:</strong> {search.fromSurface || "n/a"} m<sup>2</sup> -{" "}
              {search.toSurface || "n/a"} m<sup>2</sup>
            </p>
          </div>
          <div className="inline-flex items-center text-base font-semibold text-gray-900 dark:text-white">
            {search.distanceRadius} km
          </div>
        </div>
      </Link>
    </li>
  );
}
