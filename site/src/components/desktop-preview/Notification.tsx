interface NotificationProps {
  visible: boolean;
  title: string;
  body: string;
  icon?: string;
}

export function Notification({
  visible,
  title,
  body,
  icon = "",
}: NotificationProps) {
  if (!visible) return null;

  return (
    <div class="absolute top-16 right-4 w-72 bg-surface0/95 backdrop-blur-sm border border-surface1 rounded-xl shadow-2xl z-30 overflow-hidden animate-slide-in-right">
      <div class="p-4 flex items-start gap-3">
        <div class="text-2xl">{icon}</div>
        <div class="flex-1 min-w-0">
          <div class="font-semibold text-text text-sm">{title}</div>
          <div class="text-subtext0 text-xs mt-1">{body}</div>
        </div>
        <button class="text-overlay0 hover:text-text text-sm"></button>
      </div>

      {/* Progress bar */}
      <div class="h-0.5 bg-green animate-shrink-width" />
    </div>
  );
}
