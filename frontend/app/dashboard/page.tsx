import { cookies } from "next/headers";
import { getCookie } from "cookies-next";

async function getCategories() {
  const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

  try {
    const accessToken = getCookie("accessToken", { cookies });
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
    });
    const res_parsed = await res.json();
    const data = res_parsed.data;
    return data;
  } catch (error) {
    console.error(error);
  }
}

export default async function Test() {
  try {
    const data = await getCategories();
    const categories = data.categories;
    return (
      <div className="flex">
        <div className="fixed top-5 ml-5 border rounded-md shadow-md p-5">
          <h1 className="text-2xl font-bold">Available categories:</h1>
          {categories?.map((category) => {
            return <Category key={category.name} category={category} />;
          })}
        </div>
      </div>
    );
  } catch (error) {
    console.error(error);
  }
}

function Category({ category }: any) {
  const { name } = category || {};
  return (
    <ul className="list-none hover:bg-blue-300">
      <li className="text-xl/loose">{name}</li>
    </ul>
  );
}
