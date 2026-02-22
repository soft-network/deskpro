import Link from "next/link";
import { Mail, MessageCircle, Phone, Share2, Users, Zap } from "lucide-react";

const features = [
  {
    icon: Mail,
    title: "All Channels",
    description: "Email, chat, phone, and social media — all in one unified inbox.",
  },
  {
    icon: Users,
    title: "Multi-Tenant",
    description: "Every company gets its own isolated database — secure and scalable.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Optimized for quick response times and satisfied customers.",
  },
];

export default function LandingPage() {
  return (
    <>
      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 py-24 text-center">
        <h1 className="text-5xl font-bold tracking-tight text-gray-900">
          Support that delights.
        </h1>
        <p className="mx-auto mt-6 max-w-xl text-lg text-gray-500">
          deskpro is the helpdesk solution for modern teams — simple, fast, and
          secure. Manage all customer requests in one place.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <Link
            href="/register"
            className="rounded-md bg-gray-900 px-6 py-3 text-sm font-medium text-white hover:bg-gray-700 transition-colors"
          >
            Get Started Free
          </Link>
          <Link
            href="/login"
            className="rounded-md border border-gray-300 px-6 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Login
          </Link>
        </div>
      </section>

      {/* Channel icons */}
      <section className="border-y border-gray-100 bg-gray-50">
        <div className="mx-auto flex max-w-6xl items-center justify-center gap-12 px-6 py-8">
          {[
            { icon: Mail, label: "Email" },
            { icon: MessageCircle, label: "Chat" },
            { icon: Phone, label: "Phone" },
            { icon: Share2, label: "Social" },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex flex-col items-center gap-2 text-gray-400">
              <Icon className="h-6 w-6" />
              <span className="text-xs font-medium">{label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-24">
        <h2 className="text-center text-2xl font-bold text-gray-900 mb-12">
          Everything your team needs
        </h2>
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
          {features.map((f) => (
            <div key={f.title} className="rounded-lg border border-gray-200 p-6">
              <f.icon className="h-8 w-8 text-gray-400 mb-4" />
              <h3 className="text-base font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-sm text-gray-500 leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gray-900 py-20 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Ready to get started?</h2>
        <p className="text-gray-400 mb-8 text-sm">
          Create your account in less than 2 minutes.
        </p>
        <Link
          href="/register"
          className="rounded-md bg-white px-6 py-3 text-sm font-medium text-gray-900 hover:bg-gray-100 transition-colors"
        >
          Sign up now
        </Link>
      </section>
    </>
  );
}
