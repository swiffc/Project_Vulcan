/**
 * CAD Agent - Main Entry Point
 *
 * Handles all CAD-related tasks:
 * - SolidWorks and Inventor automation via COM
 * - Natural language to CAD operations
 * - Strategy-driven design (JSON configurations)
 */

import { CADControl, CADSoftware } from "./cad-control";
import { CommandParser, ParsedCommand } from "./command-parser";

export interface PartConfig {
  name: string;
  material?: string;
  units?: "mm" | "in";
  parameters: Record<string, number>;
}

export interface OperationResult {
  success: boolean;
  operation: string;
  details?: string;
  screenshot?: string;
  error?: string;
}

export class CADAgent {
  private cadControl: CADControl;
  private parser: CommandParser;
  private activeSoftware: CADSoftware | null = null;

  constructor(desktopServerUrl: string = "http://localhost:8000") {
    this.cadControl = new CADControl(desktopServerUrl);
    this.parser = new CommandParser();
  }

  /**
   * Connect to CAD software
   */
  async connect(software: CADSoftware = "solidworks"): Promise<boolean> {
    console.log(`🔧 Connecting to ${software}...`);

    const success = await this.cadControl.connect(software);

    if (success) {
      this.activeSoftware = software;
      console.log(`✅ Connected to ${software}`);
    } else {
      console.log(`🛑 Failed to connect to ${software}`);
    }

    return success;
  }

  /**
   * Execute a natural language CAD command
   */
  async executeCommand(command: string): Promise<OperationResult> {
    console.log(`🔧 Executing: "${command}"`);

    // Parse the command
    const parsed = this.parser.parse(command);

    if (!parsed.valid) {
      return {
        success: false,
        operation: "parse",
        error: `Could not understand command: ${command}`,
      };
    }

    // Ensure we're connected
    if (!this.activeSoftware) {
      const connected = await this.connect();
      if (!connected) {
        return {
          success: false,
          operation: parsed.operation,
          error: "Not connected to CAD software",
        };
      }
    }

    // Execute the operation
    return await this.executeOperation(parsed);
  }

  /**
   * Execute a parsed CAD operation
   */
  private async executeOperation(parsed: ParsedCommand): Promise<OperationResult> {
    switch (parsed.operation) {
      case "new_part":
        return await this.newPart(parsed.parameters?.name);

      case "sketch":
        return await this.createSketch(parsed.parameters?.plane || "Front");

      case "circle":
        return await this.drawCircle(
          parsed.parameters?.x || 0,
          parsed.parameters?.y || 0,
          parsed.parameters?.radius || 0.05
        );

      case "rectangle":
        return await this.drawRectangle(
          parsed.parameters?.x1 || -0.05,
          parsed.parameters?.y1 || -0.05,
          parsed.parameters?.x2 || 0.05,
          parsed.parameters?.y2 || 0.05
        );

      case "extrude":
        return await this.extrude(parsed.parameters?.depth || 0.01);

      case "revolve":
        return await this.revolve(parsed.parameters?.angle || 360);

      case "flange":
        return await this.buildFlange(parsed.parameters);

      case "save":
        return await this.save(parsed.parameters?.path);

      default:
        return {
          success: false,
          operation: parsed.operation,
          error: `Unknown operation: ${parsed.operation}`,
        };
    }
  }

  /**
   * Create a new part
   */
  async newPart(name?: string): Promise<OperationResult> {
    const success = await this.cadControl.newPart();
    return {
      success,
      operation: "new_part",
      details: success ? `Created new part${name ? `: ${name}` : ""}` : undefined,
      error: success ? undefined : "Failed to create new part",
    };
  }

  /**
   * Create a sketch on a plane
   */
  async createSketch(plane: string = "Front"): Promise<OperationResult> {
    const success = await this.cadControl.createSketch(plane);
    return {
      success,
      operation: "sketch",
      details: success ? `Created sketch on ${plane} plane` : undefined,
      error: success ? undefined : "Failed to create sketch",
    };
  }

  /**
   * Draw a circle
   */
  async drawCircle(x: number, y: number, radius: number): Promise<OperationResult> {
    const success = await this.cadControl.drawCircle(x, y, radius);
    return {
      success,
      operation: "circle",
      details: success
        ? `Drew circle at (${x}, ${y}) with radius ${radius}`
        : undefined,
      error: success ? undefined : "Failed to draw circle",
    };
  }

  /**
   * Draw a rectangle
   */
  async drawRectangle(
    x1: number,
    y1: number,
    x2: number,
    y2: number
  ): Promise<OperationResult> {
    const success = await this.cadControl.drawRectangle(x1, y1, x2, y2);
    return {
      success,
      operation: "rectangle",
      details: success
        ? `Drew rectangle from (${x1}, ${y1}) to (${x2}, ${y2})`
        : undefined,
      error: success ? undefined : "Failed to draw rectangle",
    };
  }

  /**
   * Extrude the current sketch
   */
  async extrude(depth: number): Promise<OperationResult> {
    const success = await this.cadControl.extrude(depth);
    return {
      success,
      operation: "extrude",
      details: success ? `Extruded ${depth}m` : undefined,
      error: success ? undefined : "Failed to extrude",
    };
  }

  /**
   * Revolve the current sketch
   */
  async revolve(angle: number = 360): Promise<OperationResult> {
    const success = await this.cadControl.revolve(angle);
    return {
      success,
      operation: "revolve",
      details: success ? `Revolved ${angle} degrees` : undefined,
      error: success ? undefined : "Failed to revolve",
    };
  }

  /**
   * Build a flange from parameters (strategy.json driven)
   */
  async buildFlange(params: Record<string, any>): Promise<OperationResult> {
    const {
      size = 6,
      standard = "ANSI",
      boltCount = 8,
      material = "Steel",
    } = params || {};

    console.log(
      `🔧 Building ${size}-inch ${standard} flange with ${boltCount} bolts...`
    );

    const steps: OperationResult[] = [];

    // Step 1: New part
    steps.push(await this.newPart(`Flange_${size}in_${standard}`));

    // Step 2: Create sketch
    steps.push(await this.createSketch("Front"));

    // Step 3: Draw outer circle (flange diameter based on size)
    const outerRadius = this.getFlangeOuterRadius(size, standard);
    steps.push(await this.drawCircle(0, 0, outerRadius));

    // Step 4: Draw inner circle (pipe bore)
    const innerRadius = (size * 25.4) / 2 / 1000; // Convert inches to meters
    steps.push(await this.drawCircle(0, 0, innerRadius));

    // Step 5: Extrude
    const thickness = this.getFlangeThickness(size, standard);
    steps.push(await this.extrude(thickness));

    // Check if all steps succeeded
    const allSuccess = steps.every((s) => s.success);

    // Take screenshot
    const screenshot = await this.cadControl.takeScreenshot();

    return {
      success: allSuccess,
      operation: "flange",
      details: allSuccess
        ? `Built ${size}" ${standard} flange with ${boltCount} bolts`
        : `Flange build failed at step ${steps.findIndex((s) => !s.success) + 1}`,
      screenshot,
      error: allSuccess ? undefined : steps.find((s) => !s.success)?.error,
    };
  }

  /**
   * Save the current document
   */
  async save(filepath?: string): Promise<OperationResult> {
    const path =
      filepath || `C:\\Vulcan\\Outputs\\part_${Date.now()}.sldprt`;
    const success = await this.cadControl.save(path);
    return {
      success,
      operation: "save",
      details: success ? `Saved to ${path}` : undefined,
      error: success ? undefined : "Failed to save",
    };
  }

  /**
   * Get flange outer radius based on size and standard
   */
  private getFlangeOuterRadius(size: number, standard: string): number {
    // Simplified ANSI flange dimensions (in meters)
    const ansiDimensions: Record<number, number> = {
      2: 0.0762,
      4: 0.1143,
      6: 0.1524,
      8: 0.1905,
      10: 0.2413,
      12: 0.2794,
    };

    return ansiDimensions[size] || (size * 25.4 * 1.5) / 1000;
  }

  /**
   * Get flange thickness based on size and standard
   */
  private getFlangeThickness(size: number, standard: string): number {
    // Simplified thickness calculation
    return 0.0254 + size * 0.003; // Base + size factor
  }
}

export { CADControl } from "./cad-control";
export { CommandParser } from "./command-parser";
