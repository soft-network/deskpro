
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper,
  SortingState,
} from "@tanstack/react-table";
import { ArrowUpDown, Search, Mail, MessageCircle, Phone, Share2 } from "lucide-react";
import { Ticket, TicketChannel } from "@/types/ticket";
import { StatusBadge, PriorityBadge } from "./status-badge";

const channelIcons: Record<TicketChannel, React.ReactNode> = {
  email: <Mail className="h-4 w-4" />,
  chat: <MessageCircle className="h-4 w-4" />,
  phone: <Phone className="h-4 w-4" />,
  social: <Share2 className="h-4 w-4" />,
};

const columnHelper = createColumnHelper<Ticket>();

const columns = [
  columnHelper.accessor("id", {
    header: "ID",
    cell: (info) => <span className="font-mono text-sm">#{info.getValue()}</span>,
  }),
  columnHelper.accessor("subject", {
    header: "Betreff",
    cell: (info) => (
      <span className="font-medium text-gray-900">{info.getValue()}</span>
    ),
  }),
  columnHelper.accessor("customerName", {
    header: "Kunde",
  }),
  columnHelper.accessor("status", {
    header: "Status",
    cell: (info) => <StatusBadge status={info.getValue()} />,
  }),
  columnHelper.accessor("priority", {
    header: "Prioritaet",
    cell: (info) => <PriorityBadge priority={info.getValue()} />,
  }),
  columnHelper.accessor("channel", {
    header: "Kanal",
    cell: (info) => (
      <div className="flex items-center gap-1.5 capitalize">
        {channelIcons[info.getValue()]}
        {info.getValue()}
      </div>
    ),
  }),
  columnHelper.accessor("assignee", {
    header: "Zugewiesen",
  }),
  columnHelper.accessor("createdAt", {
    header: "Erstellt",
    cell: (info) =>
      new Date(info.getValue()).toLocaleDateString("de-DE", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }),
  }),
];

export function TicketTable({ tickets }: { tickets: Ticket[] }) {
  const router = useRouter();
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState("");

  const table = useReactTable({
    data: tickets,
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 10 } },
  });

  return (
    <div className="space-y-4">
      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          type="text"
          placeholder="Tickets durchsuchen..."
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="w-full rounded-lg border border-gray-200 bg-white py-2 pl-10 pr-4 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-gray-200 bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="cursor-pointer select-none px-4 py-3 font-medium text-gray-600 hover:text-gray-900"
                    onClick={header.column.getToggleSortingHandler()}
                  >
                    <div className="flex items-center gap-1">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      <ArrowUpDown className="h-3.5 w-3.5 text-gray-400" />
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-gray-100">
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className="cursor-pointer hover:bg-gray-50 transition-colors"
                onClick={() => router.push(`/tickets/${row.original.id}`)}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3 whitespace-nowrap">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>
          Seite {table.getState().pagination.pageIndex + 1} von{" "}
          {table.getPageCount()}
          {" "}({table.getFilteredRowModel().rows.length} Tickets)
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            className="rounded-md border border-gray-200 bg-white px-3 py-1.5 disabled:opacity-40 hover:bg-gray-50"
          >
            Zurueck
          </button>
          <button
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            className="rounded-md border border-gray-200 bg-white px-3 py-1.5 disabled:opacity-40 hover:bg-gray-50"
          >
            Weiter
          </button>
        </div>
      </div>
    </div>
  );
}
