"use client";

import { FileText, Clock } from "lucide-react";

export default function RecentFiles() {
  const files = [
    { name: "Flange_Assembly.SLDASM", type: "Assembly", modified: "5 min ago" },
    { name: "Support_Bracket.SLDPRT", type: "Part", modified: "12 min ago" },
    { name: "Heat_Exchanger.SLDASM", type: "Assembly", modified: "1 hour ago" },
    { name: "Mounting_Plate.SLDPRT", type: "Part", modified: "2 hours ago" },
    { name: "Fan_Cover.SLDPRT", type: "Part", modified: "3 hours ago" },
  ];

  return (
    <div className="glass-base p-6">
      <h2 className="text-xl font-bold text-white mb-4">Recent Files</h2>

      <div className="space-y-2">
        {files.map((file, idx) => (
          <button
            key={idx}
            className="w-full flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-left"
          >
            <div className="flex items-center space-x-3">
              <div
                className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  file.type === "Assembly"
                    ? "bg-indigo-500/20"
                    : "bg-emerald-500/20"
                }`}
              >
                <FileText
                  className={`w-5 h-5 ${
                    file.type === "Assembly" ? "text-indigo-400" : "text-emerald-400"
                  }`}
                />
              </div>
              <div>
                <p className="text-white font-medium">{file.name}</p>
                <p className="text-sm text-gray-400">{file.type}</p>
              </div>
            </div>

            <div className="flex items-center space-x-2 text-gray-500 text-sm">
              <Clock className="w-4 h-4" />
              <span>{file.modified}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
