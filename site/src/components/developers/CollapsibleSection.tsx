import { useState, ReactNode } from "react";

interface CollapsibleSectionProps {
  title: string;
  icon: string;
  color: string;
  badge?: string;
  defaultOpen?: boolean;
  children: ReactNode;
}

export function CollapsibleSection({
  title,
  icon,
  color,
  badge,
  defaultOpen = false,
  children,
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const colorClasses: Record<
    string,
    { bg: string; text: string; border: string }
  > = {
    blue: { bg: "bg-blue/20", text: "text-blue", border: "border-blue/40" },
    green: { bg: "bg-green/20", text: "text-green", border: "border-green/40" },
    mauve: { bg: "bg-mauve/20", text: "text-mauve", border: "border-mauve/40" },
    yellow: {
      bg: "bg-yellow/20",
      text: "text-yellow",
      border: "border-yellow/40",
    },
    peach: { bg: "bg-peach/20", text: "text-peach", border: "border-peach/40" },
    sky: { bg: "bg-sky/20", text: "text-sky", border: "border-sky/40" },
    teal: { bg: "bg-teal/20", text: "text-teal", border: "border-teal/40" },
    pink: { bg: "bg-pink/20", text: "text-pink", border: "border-pink/40" },
    sapphire: {
      bg: "bg-sapphire/20",
      text: "text-sapphire",
      border: "border-sapphire/40",
    },
  };

  const colors = colorClasses[color] || colorClasses.blue;

  return (
    <div
      className={`border rounded-xl overflow-hidden transition-all ${isOpen ? colors.border : "border-surface0 hover:border-surface1"}`}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-4 flex items-center gap-4 bg-mantle hover:bg-surface0/30 transition-colors"
      >
        <span className="text-2xl">{icon}</span>
        <div className="flex-1 text-left">
          <div className="flex items-center gap-3">
            <span className={`text-lg font-bold ${colors.text}`}>{title}</span>
            {badge && (
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${colors.bg} ${colors.text}`}
              >
                {badge}
              </span>
            )}
          </div>
        </div>
        <span
          className={`text-xl transition-transform ${isOpen ? "rotate-180" : ""}`}
        >
          ▼
        </span>
      </button>

      <div
        className={`transition-all duration-300 overflow-hidden ${
          isOpen ? "max-h-[2000px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="p-6 bg-base border-t border-surface0">{children}</div>
      </div>
    </div>
  );
}
