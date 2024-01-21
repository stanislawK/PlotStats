import { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { getCookie } from "cookies-next";
import * as jose from "jose";

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

export async function middleware(req: NextRequest) {
  const res = NextResponse.next();
  const accessToken = getCookie("accessToken", { res, req });
  if (!accessToken || !tokenIsValid(accessToken, "access")) {
    const loginUrl = new URL("/", req.url);
    loginUrl.searchParams.set("loginModal", "true");
    return NextResponse.redirect(loginUrl);
  } else {
    return res;
  }
}

export const config = {
  matcher: ["/dashboard"],
};
