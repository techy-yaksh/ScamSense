import { useEffect, useRef } from "react";
import type { TranscriptMessage } from "../../lib/api";

function formatTime(ts: number) {
  if (!ts) return "";
  const d = new Date(ts > 1e11 ? ts : ts * 1000);
  return d.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function Message({ message }: { message: TranscriptMessage }) {
  if (message.role === "system") {
    const isWarning = message.warning;
    return (
      <div
        className={`border p-4 transition-colors ${
          isWarning
            ? "border-signal/60 bg-signal/10"
            : "border-line-strong bg-surface/70"
        }`}
      >
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line/60 pb-2">
          <span
            className={`font-mono text-[9px] uppercase tracking-[0.22em] font-medium ${
              isWarning ? "text-signal" : "text-ink-soft"
            }`}
          >
            {isWarning ? "Intercept // Training interrupt" : "Advisory // Analyst coach"}
          </span>
          <span className="font-mono text-[10px] text-ink-faint">
            {formatTime(message.ts)}
          </span>
        </div>
        <p className={`mt-2.5 text-sm leading-relaxed ${isWarning ? "text-ink" : "text-ink-soft"}`}>
          {message.text}
        </p>
      </div>
    );
  }

  const isUser = message.role === "user";

  return (
    <div
      className={`border transition-colors ${
        isUser
          ? "border-line-strong bg-raised/30 ml-4 sm:ml-8"
          : "border-l-2 border-l-signal border-line bg-surface/40 mr-4 sm:mr-8"
      }`}
    >
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line/50 px-4 py-2 bg-surface/30">
        <div className="flex items-center gap-2.5">
          <span
            className={`font-mono text-[9px] uppercase tracking-[0.22em] font-medium ${
              isUser ? "text-ink-soft" : "text-signal"
            }`}
          >
            {isUser ? "[DEFENDER / YOU]" : "[INTERCEPT / INCOMING CALLER]"}
          </span>
          {message.stage ? (
            <span className="font-mono text-[9px] uppercase tracking-[0.14em] text-ink-faint">
              · {message.stage}
            </span>
          ) : null}
        </div>
        <span className="font-mono text-[10px] text-ink-faint">
          {formatTime(message.ts)}
        </span>
      </div>
      <div className="px-4 py-3.5">
        <p className={`text-[14px] leading-relaxed ${isUser ? "text-ink-soft" : "text-ink"}`}>
          {message.text}
        </p>
      </div>
    </div>
  );
}

export function Transcript({
  messages,
  typing,
}: {
  messages: TranscriptMessage[];
  typing: boolean;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages.length, typing]);

  return (
    <div className="border border-line bg-bg">
      <div className="flex items-center justify-between border-b border-line bg-surface/30 px-4 py-2.5">
        <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-ink-faint">
          Forensic Telecommunication Intercept Log
        </span>
        <span className="font-mono text-[10px] text-ink-faint">
          {messages.length} {messages.length === 1 ? "entry" : "entries"} recorded
        </span>
      </div>

      <div
        ref={scrollRef}
        className="h-[460px] space-y-3.5 overflow-y-auto p-4 sm:h-[520px] sm:p-5"
      >
        {messages.map((message, i) => (
          <Message key={`${i}-${message.ts}`} message={message} />
        ))}
        {typing ? (
          <div className="flex items-center gap-3 border border-dashed border-line bg-surface/20 px-4 py-2.5">
            <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-signal">
              Channel active // Receiving incoming transmission
            </span>
            <span className="font-mono text-[10px] text-signal">_</span>
          </div>
        ) : null}
      </div>
    </div>
  );
}
