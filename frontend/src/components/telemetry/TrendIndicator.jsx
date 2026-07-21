/**
 * TrendIndicator.jsx
 *
 * Compact directional badge showing a trend arrow and classification label.
 * Used in TrendCard headers and TrendTimeline entries.
 *
 * Props:
 *   direction      {string}  "RISING" | "FALLING" | "STABLE" | "OSCILLATING" | "SPIKE_UP" | "SPIKE_DOWN"
 *   alertLevel     {string}  "NORMAL" | "WATCH" | "WARNING" | "CRITICAL"
 *   classification {string}  "Stable" | "Improving" | "Declining" | "Critical" | "Unknown"
 *   size           {string}  "sm" | "md" (default "sm")
 *   showLabel      {boolean} default true
 */

export default function TrendIndicator({
  direction     = "STABLE",
  alertLevel    = "NORMAL",
  classification = "Stable",
  size          = "sm",
  showLabel     = true,
}) {
  // ---- Arrow glyph --------------------------------------------------
  const ARROWS = {
    RISING:      "↑",
    FALLING:     "↓",
    STABLE:      "→",
    OSCILLATING: "≈",
    SPIKE_UP:    "⇑",
    SPIKE_DOWN:  "⇓",
  };
  const arrow = ARROWS[direction] || "→";

  // ---- Color palette by alert level ---------------------------------
  const PALETTE = {
    NORMAL:   { bg: "bg-emerald-50",  border: "border-emerald-200",  text: "text-emerald-700"  },
    WATCH:    { bg: "bg-yellow-50",   border: "border-yellow-200",   text: "text-yellow-700"   },
    WARNING:  { bg: "bg-orange-50",   border: "border-orange-200",   text: "text-orange-700"   },
    CRITICAL: { bg: "bg-red-50",      border: "border-red-200",      text: "text-red-700"      },
  };
  const palette = PALETTE[alertLevel] || PALETTE.NORMAL;

  const isAnimate = alertLevel === "CRITICAL";

  const textSize = size === "md" ? "text-xs" : "text-[10px]";
  const px       = size === "md" ? "px-2.5 py-1" : "px-2 py-0.5";

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border font-extrabold uppercase tracking-wider
        ${textSize} ${px}
        ${palette.bg} ${palette.border} ${palette.text}
        ${isAnimate ? "animate-pulse" : ""}
      `}
    >
      <span className="text-sm leading-none">{arrow}</span>
      {showLabel && <span>{classification}</span>}
    </span>
  );
}
