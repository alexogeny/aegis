import type { ComponentChildren } from "preact";

interface WindowProps {
  title: string;
  icon: string;
  x: number;
  y: number;
  width: number;
  height: number;
  active?: boolean;
  visible?: boolean;
  children: ComponentChildren;
}

export function Window({
  title,
  icon,
  x,
  y,
  width,
  height,
  active = true,
  visible = true,
  children,
}: WindowProps) {
  if (!visible) return null;

  return (
    <div
      class={`absolute rounded-[10px] overflow-hidden shadow-2xl animate-popin ${
        active ? "opacity-100" : "opacity-95"
      }`}
      style={{
        left: x,
        top: y,
        width,
        height,
        background: "#1e1e2e",
        border: active ? "2px solid transparent" : "2px solid #313244",
        backgroundImage: active
          ? "linear-gradient(#1e1e2e, #1e1e2e), linear-gradient(45deg, #cba6f7, #f5c2e7)"
          : undefined,
        backgroundOrigin: "border-box",
        backgroundClip: active ? "padding-box, border-box" : undefined,
      }}
    >
      {children}
    </div>
  );
}
