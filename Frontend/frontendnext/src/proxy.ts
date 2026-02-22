import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  // Redirect /dashboard shortcut to /tickets
  if (request.nextUrl.pathname === "/dashboard") {
    return NextResponse.redirect(new URL("/tickets", request.url));
  }
}

export const config = {
  matcher: ["/dashboard"],
};
