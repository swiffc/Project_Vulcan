"use client";

import { ReactNode, useState, createContext, useContext } from "react";

// Context for compound component pattern
const TabsContext = createContext<{
  value: string;
  onValueChange: (value: string) => void;
} | null>(null);

function useTabsContext() {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error("Tabs components must be used within a Tabs provider");
  }
  return context;
}

// Compound component Tabs (controlled)
interface TabsCompoundProps {
  value: string;
  onValueChange: (value: string) => void;
  children: ReactNode;
  className?: string;
}

export function Tabs({ value, onValueChange, children, className = "" }: TabsCompoundProps) {
  return (
    <TabsContext.Provider value={{ value, onValueChange }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  );
}

// TabList container
interface TabListProps {
  children: ReactNode;
  className?: string;
}

export function TabList({ children, className = "" }: TabListProps) {
  return (
    <div className={`flex gap-1 p-1 glass-dark rounded-xl mb-4 ${className}`}>
      {children}
    </div>
  );
}

// TabTrigger button
interface TabTriggerProps {
  value: string;
  children: ReactNode;
  className?: string;
}

export function TabTrigger({ value, children, className = "" }: TabTriggerProps) {
  const { value: activeValue, onValueChange } = useTabsContext();
  const isActive = activeValue === value;

  return (
    <button
      onClick={() => onValueChange(value)}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
        isActive
          ? "bg-vulcan-accent text-white"
          : "text-white/60 hover:text-white hover:bg-white/5"
      } ${className}`}
    >
      {children}
    </button>
  );
}

// TabContent panel
interface TabContentProps {
  value: string;
  children: ReactNode;
  className?: string;
}

export function TabContent({ value, children, className = "" }: TabContentProps) {
  const { value: activeValue } = useTabsContext();

  if (activeValue !== value) return null;

  return <div className={className}>{children}</div>;
}

// Simpler tab list for more control
interface TabListProps {
  tabs: { id: string; label: string; icon?: ReactNode }[];
  activeTab: string;
  onChange: (tabId: string) => void;
  className?: string;
}

export function TabList({ tabs, activeTab, onChange, className = "" }: TabListProps) {
  return (
    <div className={`flex gap-1 p-1 glass-dark rounded-xl ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            activeTab === tab.id
              ? "bg-vulcan-accent text-white"
              : "text-white/60 hover:text-white hover:bg-white/5"
          }`}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
}
