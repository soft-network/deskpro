import { Mail, MessageCircle, Phone, Share2, ShoppingBag } from "lucide-react";
import { Ticket, TicketChannel } from "@/types/ticket";
import { StatusBadge, PriorityBadge } from "./status-badge";

const channelIcons: Record<TicketChannel, React.ReactNode> = {
  email: <Mail className="h-3.5 w-3.5" />,
  chat: <MessageCircle className="h-3.5 w-3.5" />,
  phone: <Phone className="h-3.5 w-3.5" />,
  social: <Share2 className="h-3.5 w-3.5" />,
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border-b border-gray-100 py-4 px-4 last:border-0">
      <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-gray-400">
        {title}
      </h3>
      {children}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-2.5">
      <p className="text-xs text-gray-400">{label}</p>
      <div className="text-sm font-medium text-gray-800">{children}</div>
    </div>
  );
}

export function TicketSidebar({ ticket }: { ticket: Ticket }) {
  const initials = ticket.customerName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <aside className="w-68 shrink-0 overflow-y-auto border-l border-gray-200 bg-gray-50" style={{ width: "272px" }}>
      {/* Customer */}
      <Section title="Customer">
        <div className="mb-3 flex items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700">
            {initials}
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold text-gray-900">
              {ticket.customerName}
            </p>
            <p className="truncate text-xs text-gray-400">{ticket.customerEmail}</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5 text-xs capitalize text-gray-500">
          {channelIcons[ticket.channel]}
          {ticket.channel}
        </div>
      </Section>

      {/* Ticket info */}
      <Section title="Ticket">
        <div className="mb-3 flex items-center gap-2">
          <StatusBadge status={ticket.status} />
          <PriorityBadge priority={ticket.priority} />
        </div>
        <Field label="Assignee">{ticket.assignee}</Field>
        <Field label="Created">
          {new Date(ticket.createdAt).toLocaleDateString("de-DE", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
          })}
        </Field>
        {ticket.tags.length > 0 && (
          <div>
            <p className="mb-1.5 text-xs text-gray-400">Tags</p>
            <div className="flex flex-wrap gap-1">
              {ticket.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded bg-gray-200 px-1.5 py-0.5 text-xs text-gray-600"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </Section>

      {/* Orders — placeholder */}
      <Section title="Orders">
        <div className="flex flex-col items-center justify-center py-5 text-center">
          <ShoppingBag className="mb-2 h-7 w-7 text-gray-300" />
          <p className="text-xs text-gray-400">No orders linked</p>
          <p className="mt-0.5 text-xs text-gray-300">Coming soon</p>
        </div>
      </Section>
    </aside>
  );
}
