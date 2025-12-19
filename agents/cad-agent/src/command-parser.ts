/**
 * Command Parser - Natural language to CAD operations
 *
 * Parses user commands into structured CAD operations.
 */

export interface ParsedCommand {
  valid: boolean;
  operation: string;
  parameters: Record<string, any>;
  raw: string;
}

export class CommandParser {
  private patterns: Array<{
    regex: RegExp;
    operation: string;
    extractor: (match: RegExpMatchArray) => Record<string, any>;
  }>;

  constructor() {
    this.patterns = [
      // New part
      {
        regex: /(?:create|new|start)\s+(?:a\s+)?(?:new\s+)?part(?:\s+(?:called|named)\s+(.+))?/i,
        operation: "new_part",
        extractor: (match) => ({ name: match[1]?.trim() }),
      },

      // Sketch
      {
        regex: /(?:create|start|begin)\s+(?:a\s+)?sketch(?:\s+on\s+(?:the\s+)?(\w+)\s*(?:plane)?)?/i,
        operation: "sketch",
        extractor: (match) => ({ plane: match[1] || "Front" }),
      },

      // Circle
      {
        regex: /(?:draw|create|add)\s+(?:a\s+)?circle(?:\s+(?:at|with|of))?\s*(?:(?:radius|r)\s*[=:]?\s*([\d.]+))?(?:\s*(?:at|center)?\s*\(?([\d.-]+)\s*,\s*([\d.-]+)\)?)?/i,
        operation: "circle",
        extractor: (match) => ({
          radius: parseFloat(match[1]) || 0.05,
          x: parseFloat(match[2]) || 0,
          y: parseFloat(match[3]) || 0,
        }),
      },

      // Rectangle
      {
        regex: /(?:draw|create|add)\s+(?:a\s+)?(?:rectangle|rect|box)(?:\s+([\d.]+)\s*(?:x|by)\s*([\d.]+))?/i,
        operation: "rectangle",
        extractor: (match) => {
          const width = parseFloat(match[1]) || 0.1;
          const height = parseFloat(match[2]) || width;
          return {
            x1: -width / 2,
            y1: -height / 2,
            x2: width / 2,
            y2: height / 2,
          };
        },
      },

      // Extrude
      {
        regex: /extrude(?:\s+(?:by|to|depth))?\s*([\d.]+)\s*(?:mm|m|in|inch)?/i,
        operation: "extrude",
        extractor: (match) => {
          let depth = parseFloat(match[1]) || 10;
          // Convert to meters if needed
          if (match[0].includes("mm")) depth /= 1000;
          else if (match[0].includes("in")) depth *= 0.0254;
          return { depth };
        },
      },

      // Revolve
      {
        regex: /revolve(?:\s+([\d.]+)\s*(?:degrees?|deg|°)?)?/i,
        operation: "revolve",
        extractor: (match) => ({ angle: parseFloat(match[1]) || 360 }),
      },

      // Flange
      {
        regex: /(?:build|create|make)\s+(?:a\s+)?([\d.]+)\s*[-"]?\s*(?:inch|in|")?\s*(?:(\w+)\s+)?flange(?:\s+with\s+([\d]+)\s+bolts?)?/i,
        operation: "flange",
        extractor: (match) => ({
          size: parseFloat(match[1]) || 6,
          standard: match[2]?.toUpperCase() || "ANSI",
          boltCount: parseInt(match[3]) || 8,
        }),
      },

      // Save
      {
        regex: /save(?:\s+(?:as|to))?\s*(.+)?/i,
        operation: "save",
        extractor: (match) => ({ path: match[1]?.trim() }),
      },

      // Fillet
      {
        regex: /(?:add|create)\s+(?:a\s+)?fillet(?:\s+(?:of|radius|r))?\s*([\d.]+)\s*(?:mm|m)?/i,
        operation: "fillet",
        extractor: (match) => {
          let radius = parseFloat(match[1]) || 0.005;
          if (match[0].includes("mm")) radius /= 1000;
          return { radius };
        },
      },

      // Chamfer
      {
        regex: /(?:add|create)\s+(?:a\s+)?chamfer(?:\s+(?:of|distance|d))?\s*([\d.]+)\s*(?:mm|m)?/i,
        operation: "chamfer",
        extractor: (match) => {
          let distance = parseFloat(match[1]) || 0.003;
          if (match[0].includes("mm")) distance /= 1000;
          return { distance };
        },
      },

      // Pattern
      {
        regex: /(?:create|add)\s+(?:a\s+)?(?:circular|radial)\s+pattern(?:\s+(?:of|with))?\s*([\d]+)(?:\s+(?:copies|instances))?/i,
        operation: "circular_pattern",
        extractor: (match) => ({
          count: parseInt(match[1]) || 4,
          angle: 360,
        }),
      },
    ];
  }

  /**
   * Parse a natural language command
   */
  parse(command: string): ParsedCommand {
    const trimmed = command.trim();

    for (const pattern of this.patterns) {
      const match = trimmed.match(pattern.regex);
      if (match) {
        return {
          valid: true,
          operation: pattern.operation,
          parameters: pattern.extractor(match),
          raw: trimmed,
        };
      }
    }

    return {
      valid: false,
      operation: "unknown",
      parameters: {},
      raw: trimmed,
    };
  }

  /**
   * Get help text for available commands
   */
  getHelp(): string {
    return `## Available CAD Commands

### Part Creation
- \`create new part\` or \`new part called MyPart\`

### Sketching
- \`create sketch on Front plane\`
- \`draw circle radius 50mm\`
- \`draw rectangle 100 x 50\`

### Features
- \`extrude 25mm\`
- \`revolve 360 degrees\`
- \`add fillet 5mm\`
- \`add chamfer 3mm\`

### Patterns
- \`create circular pattern of 8\`

### Special
- \`build 6 inch ANSI flange with 8 bolts\`

### File
- \`save as C:\\Parts\\flange.sldprt\`
`;
  }
}
