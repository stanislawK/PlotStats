import CategoryIcon from "../ui/categoryIcon";

type Props = {
  categories: {
    name: string;
  }[];
};

export default async function CategoriesList({ categories }: Props) {
  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm dark:border-gray-700 sm:p-6 dark:bg-gray-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          All Categories:
        </h3>
      </div>
      <ul role="list" className="divide-y divide-gray-200 dark:divide-gray-700">
        {categories.map((category) => {
          return (
            <li
              className={`py-3 sm:py-4 hover:bg-gray-50 hover:pl-2 hover:transition-all`}
              key={category.name}
            >
              <div className={`flex items-center space-x-4`}>
                <div className="flex-shrink-0">
                  <CategoryIcon category={category.name}></CategoryIcon>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate dark:text-white">
                    {category.name}
                  </p>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
