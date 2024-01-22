import { NextRequest, NextFetchEvent } from "next/server";
import { NextResponse } from "next/server";
import { getCookie } from "cookies-next";
import * as jose from "jose";
import { refresh } from "./app/utils/auth";

function tokenIsValid(token: string, type: string) {
  const tokenParams = jose.decodeJwt(token);
  if (
    tokenParams.type === type &&
    !!tokenParams.exp &&
    tokenParams.exp < new Date().getTime()
  ) {
    return true;
  } else {
    return false;
  }
}

export async function middleware(req: NextRequest, event: NextFetchEvent) {
  const res = NextResponse.next();
  const accessToken = getCookie("accessToken", { res, req });
  const refreshToken = getCookie("refreshToken", { res, req });
  if (!accessToken || !tokenIsValid(accessToken, "access")) {
    if (!refreshToken || !tokenIsValid(refreshToken, "refresh")) {
      const loginUrl = new URL("/", req.url);
      loginUrl.searchParams.set("loginModal", "true");
      return NextResponse.redirect(loginUrl);
    }
    let response = NextResponse.redirect(req.url);
    await refresh(refreshToken, req, response);
    const accessToken = getCookie("accessToken", { res, req });
    if (!!accessToken) {
      return response;
    }
    if (!accessToken || !tokenIsValid(accessToken, "access")) {
      const loginUrl = new URL("/", req.url);
      loginUrl.searchParams.set("loginModal", "true");
      return NextResponse.redirect(loginUrl);
    }
  }
  return res;
}

export const config = {
  matcher: ["/dashboard"],
};
