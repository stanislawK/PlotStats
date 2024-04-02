"use server";

export async function getSearchEventsStats(
  accessToken: string,
  searchId?: number
) {
  const queryInput = searchId ? `input: {id: ${searchId}}` : "input: {}";

  const query = JSON.stringify({
    query: `
      query searchEventsStats {
        searchEventsStats(${queryInput}) {
          ... on SearchEventsStatsType {
            __typename
            searchEvents {
              id
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

export async function getSearchStats(accessToken: string, searchId?: number) {
  const queryInput = searchId ? `input: {id: ${searchId}}` : "input: {}";

  const query = JSON.stringify({
    query: `
    query searchStats {
      searchStats(${queryInput}) {
        ... on SearchStatsType {
          id
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

export async function getUserSearches(
  accessToken: string,
  withFavorite?: boolean
) {
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
            ${withFavorite ? "url" : ""}
          }
          ${withFavorite ? "favoriteId" : ""}
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
    if (data["__typename"] === "NoSearchesAvailableError") {
      return {};
    }
    return data;
  } catch (error) {
    console.log(error);
  }
}

export async function getAllSearches(accessToken: string) {
  const query = JSON.stringify({
    query: `
    query allSearches {
      allSearches {
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
            url
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
    const data = res_parsed.data["allSearches"];
    return data;
  } catch (error) {
    console.log(error);
  }
}

export async function getLastEvent(id: number, accessToken: string) {
  const query = JSON.stringify({
    query: `
    query searchEventStats {
      searchEventStats(input: {id: ${id}, topPrices: 6}) {
        ... on EventStatsType {
          id
          minPrices {
            estate {
              city
              location
              province
              street
              title
              url
            }
            areaInSquareMeters
            price
            pricePerSquareMeter
            terrainAreaInSquareMeters
          }
          minPricesPerSquareMeter {
            areaInSquareMeters
            estate {
              city
              location
              province
              street
              title
              url
            }
            price
            pricePerSquareMeter
            terrainAreaInSquareMeters
          }
        }
        ... on SearchEventDoesntExistError {
          __typename
          message
        }
        ... on NoPricesFoundError {
          __typename
          message
        }
      }
    }`,
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
    const data = res_parsed.data["searchEventStats"];
    return data;
  } catch (error) {
    console.log(error);
  }
}

export async function getLastStatuses(accessToken: string) {
  const query = JSON.stringify({
    query: `
    query lastStatus {
      searchesLastStatus {
        statuses {
          id
          status
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
    const data = res_parsed.data["searchesLastStatus"];
    return data;
  } catch (error) {
    console.log(error);
  }
}
