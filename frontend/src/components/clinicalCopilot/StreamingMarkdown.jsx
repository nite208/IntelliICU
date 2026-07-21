/**
 * StreamingMarkdown.jsx
 *
 * Enterprise-grade progressive markdown renderer for the Clinical Copilot.
 * Renders markdown in real time as tokens arrive, with a blinking cursor
 * during streaming and clean final output on completion.
 *
 * Design decisions:
 * - Uses react-markdown + remark-gfm for full GFM support (tables, task lists, etc.)
 * - Custom renderers scoped to IntelliICU design tokens (slate/cyan palette).
 * - The cursor element is appended at the DOM level, not inside the markdown
 *   tree, so the parser never sees it and there is no markdown corruption.
 * - The component is memoized: it only re-renders when text or isStreaming changes.
 */

import React, { memo, useMemo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/* -------------------------------------------------------------------------- */
/*  Custom renderers – IntelliICU design-system scoped styles                  */
/* -------------------------------------------------------------------------- */

const mdComponents = {
  // Headings
  h1: ({ children }) => (
    <h1 className="text-sm font-black text-slate-800 mt-3 mb-1.5 leading-snug">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-xs font-black text-slate-800 mt-2.5 mb-1 leading-snug uppercase tracking-wide">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-xs font-bold text-slate-700 mt-2 mb-1 leading-snug">
      {children}
    </h3>
  ),

  // Paragraphs
  p: ({ children }) => (
    <p className="text-xs text-slate-800 leading-relaxed mb-2 last:mb-0">
      {children}
    </p>
  ),

  // Bold / Italic
  strong: ({ children }) => (
    <strong className="font-bold text-slate-900">{children}</strong>
  ),
  em: ({ children }) => (
    <em className="italic text-slate-700">{children}</em>
  ),

  // Unordered list
  ul: ({ children }) => (
    <ul className="space-y-1 my-2 pl-4 list-none">{children}</ul>
  ),
  // Ordered list
  ol: ({ children }) => (
    <ol className="space-y-1 my-2 pl-4 list-decimal text-xs text-slate-800 leading-relaxed">
      {children}
    </ol>
  ),
  // List item (covers both ul and ol)
  li: ({ children }) => (
    <li className="flex items-start gap-2 text-xs text-slate-700 leading-relaxed">
      <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-cyan-500 shrink-0" />
      <span>{children}</span>
    </li>
  ),

  // Inline code
  code: ({ inline, children }) =>
    inline ? (
      <code className="px-1.5 py-0.5 rounded-md bg-slate-100 text-cyan-700 font-mono text-[10px] font-semibold">
        {children}
      </code>
    ) : (
      <code className="block w-full bg-slate-900 text-emerald-300 font-mono text-[10px] rounded-xl p-3 my-2 overflow-x-auto leading-relaxed whitespace-pre">
        {children}
      </code>
    ),

  // Fenced code block wrapper (pre)
  pre: ({ children }) => <div className="my-2">{children}</div>,

  // Blockquote
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-cyan-400 pl-3 my-2 text-xs text-slate-500 italic">
      {children}
    </blockquote>
  ),

  // Horizontal rule
  hr: () => <hr className="border-slate-200 my-3" />,

  // Table (GFM)
  table: ({ children }) => (
    <div className="overflow-x-auto my-3 rounded-xl border border-slate-200">
      <table className="w-full text-[10px] text-slate-700">{children}</table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-slate-50 border-b border-slate-200">{children}</thead>
  ),
  tbody: ({ children }) => <tbody className="divide-y divide-slate-100">{children}</tbody>,
  tr: ({ children }) => <tr>{children}</tr>,
  th: ({ children }) => (
    <th className="px-3 py-2 text-left font-black uppercase tracking-wide text-slate-500">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="px-3 py-2 font-medium">{children}</td>
  ),

  // Links
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-cyan-600 underline underline-offset-2 hover:text-cyan-800 transition-colors"
    >
      {children}
    </a>
  ),
};

/* -------------------------------------------------------------------------- */
/*  StreamingMarkdown – the exported component                                  */
/* -------------------------------------------------------------------------- */

const StreamingMarkdown = memo(
  function StreamingMarkdown({ text = "", isStreaming = false }) {
    /**
     * Memoize the ReactMarkdown tree so it only re-parses when `text` changes.
     * The cursor is rendered *outside* the memoized block so it can blink
     * without triggering a markdown re-parse on every animation frame.
     */
    const rendered = useMemo(
      () => (
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={mdComponents}
        >
          {text || ""}
        </ReactMarkdown>
      ),
      [text]
    );

    return (
      <div className="prose-clinical min-h-[1rem]">
        {rendered}
        {isStreaming && (
          <span
            aria-hidden="true"
            className="inline-block w-[2px] h-3.5 bg-cyan-500 ml-0.5 align-middle animate-[blink_0.9s_step-end_infinite] rounded-sm"
          />
        )}
      </div>
    );
  },
  // Custom comparator: only re-render when text or streaming state changes
  (prev, next) => prev.text === next.text && prev.isStreaming === next.isStreaming
);

export default StreamingMarkdown;
