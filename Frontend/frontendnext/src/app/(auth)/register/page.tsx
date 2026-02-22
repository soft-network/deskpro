"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signup } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    name: "",
    slug: "",
    admin_full_name: "",
    admin_email: "",
    admin_password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signup(form);
      router.push("/login");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8">
          <Link href="/" className="text-lg font-bold text-gray-900">
            deskpro
          </Link>
          <p className="mt-2 text-sm text-gray-500">Create your company account</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-4 bg-white border border-gray-200 rounded-lg p-6 shadow-sm"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company name
            </label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Acme Inc."
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Slug{" "}
              <span className="font-normal text-gray-400">(3–50 chars, a-z, 0-9, -)</span>
            </label>
            <input
              type="text"
              required
              value={form.slug}
              onChange={(e) => setForm({ ...form, slug: e.target.value.toLowerCase() })}
              placeholder="acme"
              pattern="^[a-z0-9-]{3,50}$"
              title="Lowercase letters, digits and hyphens only (3–50 characters)"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400"
            />
          </div>

          <hr className="border-gray-100" />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your name
            </label>
            <input
              type="text"
              value={form.admin_full_name}
              onChange={(e) => setForm({ ...form, admin_full_name: e.target.value })}
              placeholder="Jane Doe"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              required
              value={form.admin_email}
              onChange={(e) => setForm({ ...form, admin_email: e.target.value })}
              placeholder="jane@acme.com"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              required
              value={form.admin_password}
              onChange={(e) => setForm({ ...form, admin_password: e.target.value })}
              placeholder="••••••••"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400"
            />
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50 transition-colors"
          >
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500">
          Already have an account?{" "}
          <Link href="/login" className="font-medium text-gray-900 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
