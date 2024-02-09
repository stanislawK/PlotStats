export type Price = {
  estate: {
    city: string;
    location?: string;
    province?: string;
    street?: string;
    title: string;
    url: string;
  };
  areaInSquareMeters: number;
  price: number;
  pricePerSquareMeter: number;
  terrainAreaInSquareMeters?: number;
};

type PriceRowProps = {
  price: Price;
  index: number;
  isTotal: boolean;
};

export default function PriceRow({ price, index, isTotal }: PriceRowProps) {
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
        {price.estate.title}
        {", "}
        <span className="font-semibold">{price.estate.city}</span>
      </td>
      <td
        className={
          isTotal
            ? "p-4 text-sm font-semibold text-gray-900 whitespace-nowrap dark:text-white"
            : "p-4 text-sm text-gray-500 whitespace-nowrap dark:text-white"
        }
      >
        {price.price} PLN
      </td>
      <td className="p-4 text-sm font-normal text-gray-500 whitespace-nowrap dark:text-gray-400">
        {price.areaInSquareMeters} m<sup>2</sup>
      </td>
      <td
        className={
          isTotal
            ? "inline-flex items-center p-4 space-x-2 text-sm font-normal text-gray-500 whitespace-nowrap dark:text-gray-400"
            : "inline-flex items-center p-4 space-x-2 text-sm text-gray-900 whitespace-nowrap dark:text-gray-400 font-semibold"
        }
      >
        {price.pricePerSquareMeter} PLN
      </td>
      <td className="p-4 whitespace-nowrap">
        <a
          href={price.estate.url}
          className="font-medium text-blue-600 dark:text-blue-500 hover:underline"
          rel="noopener noreferrer"
          target="_blank"
        >
          Go To Offer
        </a>
      </td>
    </tr>
  );
}
