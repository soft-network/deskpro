export type TicketStatus = "open" | "pending" | "closed";
export type TicketPriority = "low" | "medium" | "high" | "urgent";
export type TicketChannel = "email" | "chat" | "phone" | "social";

export interface TicketMessage {
  id: string;
  sender: string;
  body: string;
  timestamp: string;
}

export interface Ticket {
  id: number;
  subject: string;
  customerName: string;
  customerEmail: string;
  status: TicketStatus;
  priority: TicketPriority;
  channel: TicketChannel;
  assignee: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  messages: TicketMessage[];
}
