"use client";

import { useRef, useState } from "react";
import { Bold, Italic, Underline, Paperclip, Send } from "lucide-react";
import { TicketChannel } from "@/types/ticket";

const channelLabels: Record<TicketChannel, string> = {
  email: "Email",
  chat: "Chat",
  phone: "Phone",
  social: "Social",
};

export function ReplyEditor({ channel }: { channel: TicketChannel }) {
  const editorRef = useRef<HTMLDivElement>(null);
  const [isEmpty, setIsEmpty] = useState(true);

  const exec = (command: string) => {
    document.execCommand(command, false);
    editorRef.current?.focus();
  };

  const handleInput = () => {
    setIsEmpty(editorRef.current?.textContent?.trim() === "");
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center gap-0.5 border-b border-gray-100 px-2 py-1.5">
        <button
          onMouseDown={(e) => { e.preventDefault(); exec("bold"); }}
          className="p-1.5 rounded hover:bg-gray-100 text-gray-500 hover:text-gray-800 transition-colors"
          title="Bold"
        >
          <Bold className="h-3.5 w-3.5" />
        </button>
        <button
          onMouseDown={(e) => { e.preventDefault(); exec("italic"); }}
          className="p-1.5 rounded hover:bg-gray-100 text-gray-500 hover:text-gray-800 transition-colors"
          title="Italic"
        >
          <Italic className="h-3.5 w-3.5" />
        </button>
        <button
          onMouseDown={(e) => { e.preventDefault(); exec("underline"); }}
          className="p-1.5 rounded hover:bg-gray-100 text-gray-500 hover:text-gray-800 transition-colors"
          title="Underline"
        >
          <Underline className="h-3.5 w-3.5" />
        </button>
        <div className="mx-1.5 h-4 w-px bg-gray-200" />
        <button
          className="p-1.5 rounded text-gray-300 cursor-not-allowed"
          title="Attachments (coming soon)"
          disabled
        >
          <Paperclip className="h-3.5 w-3.5" />
        </button>
      </div>

      {/* Editable area */}
      <div className="relative min-h-[100px]">
        {isEmpty && (
          <p className="pointer-events-none absolute left-3 top-3 text-sm text-gray-400">
            Reply via {channelLabels[channel]}...
          </p>
        )}
        <div
          ref={editorRef}
          contentEditable
          onInput={handleInput}
          className="min-h-[100px] p-3 text-sm text-gray-800 outline-none leading-relaxed"
          suppressContentEditableWarning
        />
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-gray-100 px-3 py-2">
        <span className="text-xs text-gray-400 capitalize">
          via {channelLabels[channel]}
        </span>
        <button className="flex items-center gap-1.5 rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 transition-colors">
          <Send className="h-3.5 w-3.5" />
          Send
        </button>
      </div>
    </div>
  );
}
