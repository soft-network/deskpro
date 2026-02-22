"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getTickets } from "@/lib/api";
import { TicketTable } from "@/components/ticket-table";
import { Ticket } from "@/types/ticket";

export default function TicketPage() {
  const router = useRouter();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTickets()
      .then(setTickets)
      .catch((err) => {
        if (err.message.includes("401")) {
          router.push("/login");
        } else {
          setError(err.message);
        }
      })
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        Laden...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-red-500">
        {error}
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Tickets</h1>
        <p className="text-sm text-gray-500 mt-1">{tickets.length} Tickets insgesamt</p>
      </div>
      <TicketTable tickets={tickets} />
    </div>
  );
}
