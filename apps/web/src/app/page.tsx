"use client";

import { Chat } from "@/components/Chat";
import { QuickCommands } from "@/components/QuickCommands";
import { StatusBar } from "@/components/StatusBar";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="glass border-b border-white/10 px-6 py-4">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-vulcan-accent to-purple-600 flex items-center justify-center">
              <span className="text-xl">V</span>
            </div>
            <div>
              <h1 className="text-xl font-bold">Project Vulcan</h1>
              <p className="text-xs text-white/50">AI Operating System</p>
            </div>
          </div>
          <StatusBar />
        </div>
      </header>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full p-4">
        <Chat />
      </div>

      {/* Quick Commands Footer */}
      <footer className="glass border-t border-white/10 px-6 py-3">
        <div className="max-w-4xl mx-auto">
          <QuickCommands />
        </div>
      </footer>
    </main>
  );
}
