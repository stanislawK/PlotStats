"use server";

export async function getCategories(accessToken: string) {
  try {
    const res = await fetch("http://backend:8000/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        query: `
        query GetCategories {
            categories {  name  }
        },
        `,
      }),
      next: { revalidate: 0 },
    });
    const res_parsed = await res.json();
    const data = res_parsed.data.categories;
    return data;
  } catch (error) {
    console.error(error);
  }
}

export async function addCategory(name: string, accessToken: string) {
  try {
    const res = await fetch("http://backend:8000/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        query: `
          mutation newCategory {
            createCategory(input: {name: "${name}"}) {
                  __typename
              ... on CategoryType {
                name
              }
              ... on CategoryExistsError {
                message
              }
              ... on InputValidationError {
                message
              }
            }
          }
          `,
      }),
    });
    const res_parsed = await res.json();
    const data = res_parsed.data.createCategory;
    return data["name"];
  } catch (error) {
    console.error(error);
  }
}
