"use server";

export async function login(email: string, password: string) {
  console.log("login...");
  const mutation = JSON.stringify({
    query: `
                mutation login {
                    login(input: {
                            email: "${email}", password: "${password}"
                        }) {
                        __typename
                        ... on JWTPair {
                            accessToken
                            refreshToken
                        }
                        ... on LoginUserError {
                            __typename
                            message
                        }
                        ... on InputValidationError {
                            __typename
                            message
                        }
                    }
                }
            `,
  });
  try {
    console.log("fetching...");
    const res = await fetch("http://backend:8000/graphql", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
      },
      body: mutation,
    });
    const res_parsed = await res.json();
    const data = res_parsed.data;
    if (data === undefined || data.login.__typename === "LoginUserError") {
      console.log("Can't login");
    } else {
      const accessToken = data.login.accessToken;
      const refreshToken = data.login.refreshToken;
      console.log(accessToken);
      console.log(refreshToken);
    }
    console.log(data);
  } catch (error) {
    console.log(error);
  }
}
