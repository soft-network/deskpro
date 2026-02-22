import { TicketStatus, TicketPriority } from "@/types/ticket";

const statusColors: Record<TicketStatus, string> = {
  open: "bg-green-100 text-green-800",
  pending: "bg-yellow-100 text-yellow-800",
  closed: "bg-gray-100 text-gray-600",
};

const priorityColors: Record<TicketPriority, string> = {
  low: "bg-blue-100 text-blue-700",
  medium: "bg-orange-100 text-orange-700",
  high: "bg-red-100 text-red-700",
  urgent: "bg-red-200 text-red-900 font-semibold",
};

export function StatusBadge({ status }: { status: TicketStatus }) {
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${statusColors[status]}`}
    >
      {status}
    </span>
  );
}

export function PriorityBadge({ priority }: { priority: TicketPriority }) {
  return (
    <span
      className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${priorityColors[priority]}`}
    >
      {priority}
    </span>
  );
}
