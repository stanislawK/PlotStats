import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import * as jose from "jose";

function tokenIsValid(token: string, type: string) {
  const tokenParams = jose.decodeJwt(token);
  console.log(tokenParams);
  console.log(new Date().getTime());
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
  const parsedUrl = req.nextUrl;
  if (parsedUrl.pathname === "/") {
    return;
  }
  const accessToken = cookies().get("accessToken")?.value;
  if (!accessToken || !tokenIsValid(accessToken, "access")) {
    return NextResponse.rewrite(new URL("/?loginModal=true", req.url));
  } else {
    return;
  }
}

export const config = {
  matcher: ["/((?!_next|fonts|[\\w-]+\\.\\w+).*)"],
};
