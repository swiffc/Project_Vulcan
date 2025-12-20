"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "../ui/Card";
import { Button } from "../ui/Button";

interface Part {
  id: string;
  partNumber: string;
  name: string;
  material: string;
  category: string;
}

const mockParts: Part[] = [
  { id: "1", partNumber: "BRK-001", name: "L-Bracket Standard", material: "Steel", category: "Brackets" },
  { id: "2", partNumber: "HSG-045", name: "Motor Housing", material: "Aluminum", category: "Housings" },
  { id: "3", partNumber: "PLT-012", name: "Base Plate 6x6", material: "Steel", category: "Plates" },
  { id: "4", partNumber: "ROD-008", name: "Drive Shaft", material: "Steel", category: "Shafts" },
];

export function PartsLibrary() {
  const [parts] = useState<Part[]>(mockParts);
  const [search, setSearch] = useState("");

  const filtered = parts.filter(p => 
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.partNumber.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4 mt-4">
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Search parts..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30"
        />
        <Button variant="primary">+ Add Part</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((part) => (
          <Card key={part.id} className="hover:border-vulcan-accent/50 transition-colors cursor-pointer">
            <CardContent className="p-4">
              <p className="font-mono text-vulcan-accent text-sm">{part.partNumber}</p>
              <h3 className="font-medium text-white mt-1">{part.name}</h3>
              <div className="flex justify-between mt-2 text-sm text-white/50">
                <span>{part.material}</span>
                <span>{part.category}</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
