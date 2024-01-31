"use server";

export async function getFavSearchEventsStats(accessToken: string) {
  const query = JSON.stringify({
    query: `
      query searchEventsStats {
        searchEventsStats {
          ... on SearchEventsStatsType {
            __typename
            searchEvents {
              avgAreaInSquareMeters
              avgPrice
              avgPricePerSquareMeter
              avgTerrainAreaInSquareMeters
              date
              minPrice {
                price
                pricePerSquareMeter
              }
              minPricePerSquareMeter {
                areaInSquareMeters
                price
                pricePerSquareMeter
              }
            }
          }
          ... on FavoriteSearchDoesntExistError {
            __typename
            message
          }
          ... on NoSearchEventError {
            __typename
            message
          }
          ... on NoPricesFoundError {
            __typename
            message
          }
        }
      }
              `,
  });
  try {
    const api_res = await fetch("http://backend:8000/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        Authorization: `Bearer ${accessToken}`,
      },
      body: query,
    });
    const res_parsed = await api_res.json();
    const data = res_parsed.data;
    return data;
  } catch (error) {
    console.log(error);
  }
}

export async function getSearchStats(accessToken: string) {
  const query = JSON.stringify({
    query: `
    query searchStats {
      searchStats(input: {}) {
        ... on SearchStatsType {
          avgAreaTotal
          avgPricePerSquareMeterTotal
          avgPriceTotal
          category {
            name
          }
          dateFrom
          dateTo
          distanceRadius
          fromPrice
          fromSurface
          location
          toPrice
          toSurface
        }
        ... on SearchDoesntExistError {
          __typename
        }
      }
    }
    `,
  });
  try {
    const api_res = await fetch("http://backend:8000/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        Authorization: `Bearer ${accessToken}`,
      },
      body: query,
    });
    const res_parsed = await api_res.json();
    const data = res_parsed.data["searchStats"];
    return data;
  } catch (error) {
    console.log(error);
  }
}

export async function getUserSearches(accessToken: string) {
  const query = JSON.stringify({
    query: `
    query usersSearches {
      usersSearches {
        ... on SearchesType {
          __typename
          searches {
            category {
              name
            }
            distanceRadius
            fromPrice
            fromSurface
            id
            location
            toPrice
            toSurface
          }
        }
        ... on NoSearchesAvailableError {
          __typename
          message
        }
      }
    }
    `,
  });
  try {
    const api_res = await fetch("http://backend:8000/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        Authorization: `Bearer ${accessToken}`,
      },
      body: query,
    });
    const res_parsed = await api_res.json();
    const data = res_parsed.data["usersSearches"];
    return data;
  } catch (error) {
    console.log(error);
  }
}
