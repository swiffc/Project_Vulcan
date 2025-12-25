/**
 * Rules Loader - Loads and parses RULES.md for system prompts
 *
 * Provides rule-aware system prompts for all agents.
 * Caches parsed rules for performance.
 */

import { readFileSync, existsSync } from "fs";
import { join } from "path";

interface Rule {
  number: number;
  name: string;
  content: string;
  section: string;
  priority: "critical" | "high" | "normal" | "low";
}

interface Section {
  number: number;
  name: string;
  rules: Rule[];
}

interface ParsedRules {
  sections: Section[];
  rules: Rule[];
  fileHash: string;
  parsedAt: Date;
}

// Cache for parsed rules
let cachedRules: ParsedRules | null = null;
let cachedFileHash: string | null = null;

/**
 * Get path to RULES.md
 */
function getRulesPath(): string {
  // Try multiple locations
  const paths = [
    join(process.cwd(), "../../RULES.md"),
    join(process.cwd(), "../../../RULES.md"),
    join(process.cwd(), "RULES.md"),
    "C:/Users/DCornealius/Documents/GitHub/Project_Vulcan_Fresh/RULES.md"
  ];

  for (const p of paths) {
    if (existsSync(p)) {
      return p;
    }
  }

  throw new Error("RULES.md not found");
}

/**
 * Parse RULES.md into structured sections and rules
 */
export function parseRules(forceRefresh = false): ParsedRules {
  // Return cached if available
  if (cachedRules && !forceRefresh) {
    return cachedRules;
  }

  const rulesPath = getRulesPath();
  const content = readFileSync(rulesPath, "utf-8");

  const sections: Section[] = [];
  const rules: Rule[] = [];

  // Parse sections and rules
  const lines = content.split("\n");
  let currentSection: Section | null = null;
  let currentRule: Rule | null = null;
  let ruleContent: string[] = [];

  const sectionPattern = /^## SECTION (\d+): (.+)$/;
  const rulePattern = /^### Rule (\d+): (.+)$/;

  for (const line of lines) {
    const sectionMatch = line.match(sectionPattern);
    if (sectionMatch) {
      // Save previous rule
      if (currentRule) {
        currentRule.content = ruleContent.join("\n").trim();
        currentRule.priority = detectPriority(currentRule.content, currentRule.name);
        rules.push(currentRule);
        if (currentSection) {
          currentSection.rules.push(currentRule);
        }
      }

      // Save previous section
      if (currentSection) {
        sections.push(currentSection);
      }

      // Start new section
      currentSection = {
        number: parseInt(sectionMatch[1]),
        name: sectionMatch[2].trim(),
        rules: [],
      };
      currentRule = null;
      ruleContent = [];
      continue;
    }

    const ruleMatch = line.match(rulePattern);
    if (ruleMatch) {
      // Save previous rule
      if (currentRule) {
        currentRule.content = ruleContent.join("\n").trim();
        currentRule.priority = detectPriority(currentRule.content, currentRule.name);
        rules.push(currentRule);
        if (currentSection) {
          currentSection.rules.push(currentRule);
        }
      }

      // Start new rule
      currentRule = {
        number: parseInt(ruleMatch[1]),
        name: ruleMatch[2].trim(),
        content: "",
        section: currentSection?.name || "Unknown",
        priority: "normal",
      };
      ruleContent = [];
      continue;
    }

    // Accumulate rule content
    if (currentRule) {
      ruleContent.push(line);
    }
  }

  // Save final rule and section
  if (currentRule) {
    currentRule.content = ruleContent.join("\n").trim();
    currentRule.priority = detectPriority(currentRule.content, currentRule.name);
    rules.push(currentRule);
    if (currentSection) {
      currentSection.rules.push(currentRule);
    }
  }
  if (currentSection) {
    sections.push(currentSection);
  }

  // Cache results
  cachedRules = {
    sections,
    rules,
    fileHash: simpleHash(content),
    parsedAt: new Date(),
  };

  return cachedRules;
}

/**
 * Detect rule priority from content
 */
function detectPriority(content: string, name: string): "critical" | "high" | "normal" | "low" {
  const text = content + " " + name;

  if (/CRITICAL|MANDATORY|MUST|ABSOLUTE|NEVER|ALWAYS/i.test(text)) {
    return "critical";
  }
  if (/IMPORTANT|REQUIRED|SHOULD/i.test(text)) {
    return "high";
  }
  if (/optional|may|consider/i.test(text)) {
    return "low";
  }
  return "normal";
}

/**
 * Simple hash for cache invalidation
 */
function simpleHash(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(16);
}

/**
 * Get rules for a specific agent type
 */
export function getRulesForAgent(agentType: string): Rule[] {
  const { rules } = parseRules();

  const agentKeywords: Record<string, string[]> = {
    cad: ["cad", "solidworks", "inventor", "flange", "part", "assembly", "asme", "plan"],
    trading: ["trade", "trading", "forex", "gbp", "ict", "btmm"],
    work: ["work", "j2", "tracker", "excel", "outlook"],
    general: [],
  };

  const keywords = agentKeywords[agentType] || [];

  return rules.filter((rule) => {
    // Include critical rules for all agents
    if (rule.priority === "critical") {
      return true;
    }

    // Check if rule applies to this agent
    const ruleText = (rule.content + " " + rule.name).toLowerCase();
    return keywords.some((kw) => ruleText.includes(kw));
  });
}

/**
 * Get critical rules
 */
export function getCriticalRules(): Rule[] {
  const { rules } = parseRules();
  return rules.filter((r) => r.priority === "critical");
}

/**
 * Get a specific section
 */
export function getSection(sectionNum: number): Section | undefined {
  const { sections } = parseRules();
  return sections.find((s) => s.number === sectionNum);
}

/**
 * Generate system prompt with rules for an agent
 */
export function generateRulesPrompt(
  agentType: string,
  includeSections?: number[],
  maxTokens = 3000
): string {
  const rules = parseRules();
  const parts: string[] = [
    "# PROJECT RULES (From RULES.md)",
    "",
    "You MUST follow these rules. Violations are not acceptable.",
    "",
  ];

  let charCount = 0;
  const maxChars = maxTokens * 4;

  // Add critical rules first
  const critical = getCriticalRules();
  if (critical.length > 0) {
    parts.push("## CRITICAL RULES (Must Follow)");
    parts.push("");
    for (const rule of critical.slice(0, 5)) {
      const ruleText = `**Rule ${rule.number}: ${rule.name}**\n${rule.content.slice(0, 400)}${rule.content.length > 400 ? "..." : ""}`;
      if (charCount + ruleText.length > maxChars) break;
      parts.push(ruleText);
      parts.push("");
      charCount += ruleText.length;
    }
  }

  // Add agent-specific rules
  const agentRules = getRulesForAgent(agentType);
  if (agentRules.length > 0) {
    parts.push(`## ${agentType.toUpperCase()} Agent Rules`);
    parts.push("");
    for (const rule of agentRules.slice(0, 10)) {
      if (rule.priority === "critical") continue; // Already added
      const ruleText = `**Rule ${rule.number}: ${rule.name}**\n${rule.content.slice(0, 300)}${rule.content.length > 300 ? "..." : ""}`;
      if (charCount + ruleText.length > maxChars) break;
      parts.push(ruleText);
      parts.push("");
      charCount += ruleText.length;
    }
  }

  // Add specific sections if requested
  if (includeSections) {
    for (const sectionNum of includeSections) {
      const section = getSection(sectionNum);
      if (section) {
        parts.push(`## Section ${section.number}: ${section.name}`);
        parts.push("");
        for (const rule of section.rules.slice(0, 5)) {
          const ruleText = `**Rule ${rule.number}: ${rule.name}**\n${rule.content.slice(0, 300)}${rule.content.length > 300 ? "..." : ""}`;
          if (charCount + ruleText.length > maxChars) break;
          parts.push(ruleText);
          parts.push("");
          charCount += ruleText.length;
        }
      }
    }
  }

  // Add acknowledgment requirement
  parts.push("---");
  parts.push("**ACKNOWLEDGMENT**: Before starting any task, state: 'Checked RULES.md - relevant sections: [X, Y, Z]'");

  return parts.join("\n");
}

/**
 * Generate CAD-specific system prompt with rules
 */
export function getCADRulesPrompt(): string {
  return generateRulesPrompt("cad", [0, 7, 10], 4000);
}

/**
 * Get rules summary for display
 */
export function getRulesSummary(): {
  totalSections: number;
  totalRules: number;
  criticalRules: number;
  parsedAt: Date;
} {
  const { sections, rules, parsedAt } = parseRules();
  return {
    totalSections: sections.length,
    totalRules: rules.length,
    criticalRules: rules.filter((r) => r.priority === "critical").length,
    parsedAt,
  };
}
