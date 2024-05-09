type PriceChangeProps = {
  allAvgPrices: number[];
};

function getPriceChange(allAvgPrices: number[]) {
  if (allAvgPrices.length < 2) {
    return 0;
  }
  const thisWeekPrice: number = allAvgPrices[allAvgPrices.length - 1];
  const avgTotal =
    allAvgPrices.reduce((a, b) => a + b, 0) / allAvgPrices.length;
  if (thisWeekPrice == avgTotal) {
    return 0;
  }
  // @ts-ignore
  return +(Math.round((thisWeekPrice / avgTotal - 1) * 100 + "e+2") + "e-2");
}

export default function PriceChange({ allAvgPrices }: PriceChangeProps) {
  const percentage = getPriceChange(allAvgPrices);
  if (percentage > 0) {
    return (
      <div className="flex items-center justify-end flex-1 text-base font-medium text-red-500 dark:text-red-400">
        {percentage}%
        <svg
          className="w-5 h-5"
          fill="currentColor"
          viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fillRule="evenodd"
            d="M5.293 7.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L6.707 7.707a1 1 0 01-1.414 0z"
            clipRule="evenodd"
          ></path>
        </svg>
      </div>
    );
  }
  return (
    <div className="flex items-center justify-end flex-1 text-base font-medium text-green-500 dark:text-green-400">
      {percentage}%
      <svg
        className="w-5 h-5 pb-1"
        xmlns="http://www.w3.org/2000/svg"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          d="M12 19V5m0 14-4-4m4 4 4-4"
        />
      </svg>
    </div>
  );
}
