import { cookies } from "next/headers";
import { redirect, notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Mail, MessageCircle, Phone, Share2 } from "lucide-react";
import { StatusBadge, PriorityBadge } from "@/components/status-badge";
import { TicketSidebar } from "@/components/ticket-sidebar";
import { ReplyEditor } from "@/components/reply-editor";
import { Ticket, TicketChannel } from "@/types/ticket";

// Server components: prefer BACKEND_URL (Docker internal service name) so
// container-to-container requests don't leave the Docker network.
// Falls back to NEXT_PUBLIC_API_URL for local dev without Docker.
const API_BASE =
  process.env.BACKEND_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000/api";

const channelIcons: Record<TicketChannel, React.ReactNode> = {
  email: <Mail className="h-4 w-4" />,
  chat: <MessageCircle className="h-4 w-4" />,
  phone: <Phone className="h-4 w-4" />,
  social: <Share2 className="h-4 w-4" />,
};

async function fetchTicket(id: number): Promise<Ticket | null> {
  // Forward the browser's auth cookies so Django's TenantMiddleware
  // can resolve the tenant context and validate the JWT.
  const cookieStore = await cookies();
  const res = await fetch(`${API_BASE}/tickets/${id}`, {
    headers: { Cookie: cookieStore.toString() },
    cache: "no-store",
  });

  if (res.status === 401) return null;   // unauthenticated → redirect to login
  if (res.status === 404) return undefined as unknown as null; // trigger notFound()
  if (!res.ok) throw new Error(`Failed to fetch ticket ${id}: ${res.status}`);

  return res.json();
}

export default async function TicketDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const ticket = await fetchTicket(Number(id));

  if (ticket === null) redirect("/login");
  if (!ticket) notFound();

  return (
    <div className="flex h-full flex-col">
      {/* Header bar */}
      <div className="flex shrink-0 items-center gap-3 border-b border-gray-200 bg-white px-4 py-2.5">
        <Link
          href="/tickets"
          className="flex items-center text-gray-400 hover:text-gray-700 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
        </Link>

        <span className="font-mono text-xs text-gray-400">#{ticket.id}</span>
        <h1 className="flex-1 truncate text-sm font-semibold text-gray-900">
          {ticket.subject}
        </h1>

        <div className="flex shrink-0 items-center gap-2">
          <StatusBadge status={ticket.status} />
          <PriorityBadge priority={ticket.priority} />
          <div className="ml-1 flex items-center gap-1.5 text-xs capitalize text-gray-400">
            {channelIcons[ticket.channel]}
            {ticket.channel}
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Main: messages + editor */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto px-6 py-5 space-y-3">
            {ticket.messages.map((message) => {
              const isCustomer = message.sender === ticket.customerName;
              return (
                <div key={message.id} className="rounded-lg border border-gray-200 bg-white">
                  <div className="flex items-center justify-between border-b border-gray-100 px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gray-100 text-xs font-semibold text-gray-600">
                        {message.sender[0].toUpperCase()}
                      </div>
                      <span className="text-sm font-semibold text-gray-800">
                        {message.sender}
                      </span>
                      {!isCustomer && (
                        <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-600">
                          Agent
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(message.timestamp).toLocaleDateString("de-DE", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                  <p className="px-4 py-3 text-sm leading-relaxed text-gray-700">
                    {message.body}
                  </p>
                </div>
              );
            })}
          </div>

          <div className="shrink-0 border-t border-gray-200 p-4">
            <ReplyEditor channel={ticket.channel} />
          </div>
        </div>

        <TicketSidebar ticket={ticket} />
      </div>
    </div>
  );
}
