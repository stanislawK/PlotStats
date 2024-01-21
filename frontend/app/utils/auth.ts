"use server";

import { cookies } from "next/headers";
import { setCookie, getCookie } from "cookies-next";
import * as jose from "jose";

function getTimeToExpire(token: string) {
  const tokenParams = jose.decodeJwt(token);
  if (!!tokenParams.exp) {
    const currTimestampSec = Math.floor(new Date().getTime() / 1000);
    const toExp = tokenParams.exp - currTimestampSec;
    if (toExp < 0) {
      return 0;
    }
    return toExp;
  }
  return 0;
}

export async function login(email: string, password: string) {
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
    if (
      data === undefined ||
      data.login.__typename === "LoginUserError" ||
      !data.login.accessToken
    ) {
      console.log("Can't login");
    } else {
      const accessToken = data.login.accessToken;
      const refreshToken = data.login.refreshToken;
      setCookie("accessToken", accessToken, {
        cookies,
        maxAge: getTimeToExpire(accessToken),
        httpOnly: true,
      });
      setCookie("refreshToken", refreshToken, {
        cookies,
        maxAge: getTimeToExpire(refreshToken),
        httpOnly: true,
      });
    }
  } catch (error) {
    console.log(error);
  }
}
