"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderOpen,
  FileText,
  Box,
  Package,
  GitBranch,
  ListChecks,
  Upload,
  Activity,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface NavItem {
  name: string;
  href: string;
  icon: any;
}

const navItems: NavItem[] = [
  { name: "Dashboard", href: "/cad/dashboard", icon: LayoutDashboard },
  { name: "Projects", href: "/cad/projects", icon: FolderOpen },
  { name: "Drawings", href: "/cad/drawings/search", icon: FileText },
  { name: "Assemblies", href: "/cad/assemblies", icon: Box },
  { name: "Parts Library", href: "/cad/parts/library", icon: Package },
  { name: "ECN Tracker", href: "/cad/ecn", icon: GitBranch },
  { name: "Job Queue", href: "/cad/jobs/queue", icon: ListChecks },
  { name: "Exports", href: "/cad/exports", icon: Upload },
  { name: "Performance", href: "/cad/performance", icon: Activity },
  { name: "Settings", href: "/cad/settings", icon: Settings },
];

interface Props {
  isOpen: boolean;
  onToggle: () => void;
}

export default function CADNav({ isOpen, onToggle }: Props) {
  const pathname = usePathname();

  return (
    <nav
      className={cn(
        "glass-base border-r border-white/10 transition-all duration-300",
        isOpen ? "w-64" : "w-20"
      )}
    >
      {/* Toggle Button */}
      <div className="flex justify-end p-4">
        <button
          onClick={onToggle}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors"
        >
          {isOpen ? (
            <ChevronLeft className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-400" />
          )}
        </button>
      </div>

      {/* Navigation Items */}
      <div className="px-3 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all",
                isActive
                  ? "glass-accent text-white font-medium"
                  : "text-gray-400 hover:bg-white/5 hover:text-white"
              )}
            >
              <Icon className={cn("w-5 h-5 flex-shrink-0", isActive && "text-indigo-400")} />
              {isOpen && <span className="truncate">{item.name}</span>}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
