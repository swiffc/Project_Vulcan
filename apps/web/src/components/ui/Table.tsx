"use client";

import { ReactNode } from "react";

interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (item: T) => ReactNode;
  className?: string;
}

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
  className?: string;
}

export function Table<T extends { id?: string | number }>({
  data,
  columns,
  onRowClick,
  emptyMessage = "No data available",
  className = "",
}: TableProps<T>) {
  const getValue = (item: T, key: string): ReactNode => {
    const keys = key.split(".");
    let value: any = item;
    for (const k of keys) {
      value = value?.[k];
    }
    return value;
  };

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full">
        <thead>
          <tr className="border-b border-white/10">
            {columns.map((col) => (
              <th
                key={String(col.key)}
                className={`px-4 py-3 text-left text-xs font-semibold text-white/50 uppercase tracking-wider ${col.className || ""}`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-8 text-center text-white/30"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((item, index) => (
              <tr
                key={item.id || index}
                onClick={() => onRowClick?.(item)}
                className={`border-b border-white/5 ${
                  onRowClick ? "cursor-pointer hover:bg-white/5" : ""
                }`}
              >
                {columns.map((col) => (
                  <td
                    key={String(col.key)}
                    className={`px-4 py-3 text-sm text-white/80 ${col.className || ""}`}
                  >
                    {col.render ? col.render(item) : getValue(item, String(col.key))}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

// Simple data list for activity feeds
interface DataListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => ReactNode;
  emptyMessage?: string;
  className?: string;
}

export function DataList<T>({
  items,
  renderItem,
  emptyMessage = "No items",
  className = "",
}: DataListProps<T>) {
  if (items.length === 0) {
    return (
      <div className={`text-center py-8 text-white/30 ${className}`}>
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className={`divide-y divide-white/5 ${className}`}>
      {items.map((item, index) => renderItem(item, index))}
    </div>
  );
}

// Primitive table components for custom table layouts
interface TablePrimitiveProps {
  children: ReactNode;
  className?: string;
}

export function TableHeader({ children, className = "" }: TablePrimitiveProps) {
  return <thead className={className}>{children}</thead>;
}

export function TableBody({ children, className = "" }: TablePrimitiveProps) {
  return <tbody className={className}>{children}</tbody>;
}

interface TableRowProps extends TablePrimitiveProps {
  onClick?: () => void;
}

export function TableRow({ children, className = "", onClick }: TableRowProps) {
  return (
    <tr
      onClick={onClick}
      className={`border-b border-white/5 ${onClick ? "cursor-pointer hover:bg-white/5" : ""} ${className}`}
    >
      {children}
    </tr>
  );
}

export function TableHead({ children, className = "" }: TablePrimitiveProps) {
  return (
    <th className={`px-4 py-3 text-left text-xs font-semibold text-white/50 uppercase tracking-wider ${className}`}>
      {children}
    </th>
  );
}

export function TableCell({ children, className = "" }: TablePrimitiveProps) {
  return (
    <td className={`px-4 py-3 text-sm text-white/80 ${className}`}>
      {children}
    </td>
  );
}
