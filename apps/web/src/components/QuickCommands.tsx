"use client";

const QUICK_COMMANDS = [
  { label: "Build Flange", command: "Build a 6-inch ANSI flange with 8 bolts", icon: "🔧" },
  { label: "Scan GBP/USD", command: "Scan GBP/USD for Q2 setup", icon: "📈" },
  { label: "Scan XAUUSD", command: "Scan XAUUSD for ICT setup", icon: "🥇" },
  { label: "Weekly Review", command: "Generate weekly trading review", icon: "📊" },
  { label: "Take Screenshot", command: "Take a screenshot of the current screen", icon: "📸" },
];

export function QuickCommands() {
  const handleCommand = (command: string) => {
    // Dispatch custom event to send command
    const event = new CustomEvent("vulcan:command", { detail: command });
    window.dispatchEvent(event);
  };

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-1">
      <span className="text-xs text-white/40 shrink-0">Quick:</span>
      {QUICK_COMMANDS.map((cmd) => (
        <button
          key={cmd.label}
          onClick={() => handleCommand(cmd.command)}
          className="shrink-0 px-3 py-1.5 rounded-full text-xs bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all flex items-center gap-1.5"
        >
          <span>{cmd.icon}</span>
          <span>{cmd.label}</span>
        </button>
      ))}
    </div>
  );
}
