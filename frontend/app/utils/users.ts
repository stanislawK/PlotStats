"use server";
import * as jose from "jose";

export async function isAdminUser(token: string) {
  const tokenParams = jose.decodeJwt(token);
  if (!tokenParams?.roles) {
    return false;
  }
  const roles = Array.from(tokenParams.roles);
  if (roles.length > 0) {
    return roles.includes("admin");
  }
  return false;
}

export async function isTokenFresh(token: string) {
  const tokenParams = jose.decodeJwt(token);
  if (!tokenParams?.fresh) {
    return false;
  }
  return tokenParams.fresh == true;
}

export async function getUsers(accessToken: string) {
  if (!(await isAdminUser(accessToken))) {
    return [];
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

export async function registerUsers(accessToken: string, email: string) {
  if (!isAdminUser(accessToken)) {
    return "Failed to register a new user";
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
        mutation registerUser {
          registerUser(input: {email: "${email}"}) {
            ... on RegisterResponse {
              __typename
              temporaryPassword
            }
            ... on UserExistsError {
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
      }),
    });
    const res_parsed = await res.json();
    const data = res_parsed.data.registerUser.temporaryPassword;
    return data;
  } catch (error) {
    console.error(error);
  }
}

export async function deactivateUser(accessToken: string, email: string) {
  if (!isAdminUser(accessToken)) {
    return "Failed to deactivate user"
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
        mutation deactivateUser {
          deactivateUser(input: {email: "${email}"}) {
            ... on DeactivateAccountSuccess {
              __typename
              message
            }
            ... on DeactivateAccountError {
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
      }),
    });
    const res_parsed = await res.json();
    const data = res_parsed.data.deactivateUser;
    return data["__typename"] == "DeactivateAccountSuccess";
  } catch (error) {
    console.error(error);
  }
}
