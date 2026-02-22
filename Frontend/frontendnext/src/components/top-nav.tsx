"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown, LogOut, User } from "lucide-react";
import { getMe, logout } from "@/lib/api";

export default function TopNav() {
  const router = useRouter();
  const [user, setUser] = useState<{ email: string; full_name: string } | null>(null);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getMe().then(setUser);
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  const displayName = user?.full_name || user?.email || "Account";
  const initials = displayName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="flex h-12 shrink-0 items-center justify-end border-b border-gray-200 bg-white px-4">
      <div className="relative" ref={ref}>
        <button
          onClick={() => setOpen((v) => !v)}
          className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gray-200 text-xs font-semibold text-gray-600">
            {user ? initials : <User className="h-3.5 w-3.5" />}
          </div>
          <span className="max-w-[140px] truncate">{displayName}</span>
          <ChevronDown className="h-3.5 w-3.5 text-gray-400" />
        </button>

        {open && (
          <div className="absolute right-0 top-full mt-1 w-44 rounded-md border border-gray-200 bg-white shadow-md z-50">
            {user && (
              <div className="border-b border-gray-100 px-3 py-2">
                <p className="truncate text-xs font-medium text-gray-900">{user.full_name}</p>
                <p className="truncate text-xs text-gray-400">{user.email}</p>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
