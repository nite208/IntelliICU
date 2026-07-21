import React, { useState } from "react";
import { Send } from "lucide-react";

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim() || disabled) return;
    onSend(text.trim());
    setText("");
  };

  return (
    <form onSubmit={handleSubmit} className="relative flex items-center gap-2">
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={disabled}
        placeholder={disabled ? "Analyzing chart context..." : "Ask a clinical question about this patient..."}
        className="w-full text-xs bg-slate-50 border border-slate-200 rounded-2xl py-3.5 pl-4 pr-12 text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-cyan-600 transition disabled:opacity-60"
      />
      <button
        type="submit"
        disabled={disabled || !text.trim()}
        className="absolute right-2.5 p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white transition disabled:bg-slate-200 disabled:text-slate-400"
      >
        <Send size={14} />
      </button>
    </form>
  );
}
