"use server";
import * as jose from "jose";

function isAdminUser(token: string) {
    const tokenParams = jose.decodeJwt(token);
    if (!tokenParams?.roles) {
      return false
    }
    const roles = Array.from(tokenParams.roles)
    if (roles.length > 0) {
      return roles.includes("admin")
    }
    return false;
  }

export async function getUsers(accessToken: string) {
  if (!isAdminUser(accessToken)) {
    return []
  }
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
        query allUsers {
            allUsers {
              users {
                email
                id
                isActive
                roles
              }
            }
          }
        `,
      }),
      next: { revalidate: 0 },
    });
    const res_parsed = await res.json();
    const data = res_parsed.data.allUsers.users;
    return data;
  } catch (error) {
    console.error(error);
  }
}
