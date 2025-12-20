/**
 * CAD Control - Desktop automation for SolidWorks/Inventor
 *
 * Communicates with the Desktop Server's COM endpoints
 * to control CAD software.
 */

export type CADSoftware = "solidworks" | "inventor";

interface DesktopResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

export class CADControl {
  private baseUrl: string;
  private software: CADSoftware = "solidworks";

  constructor(desktopServerUrl: string = "http://localhost:8000") {
    this.baseUrl = desktopServerUrl;
  }

  private async fetch<T>(
    endpoint: string,
    method: "GET" | "POST" = "POST",
    body?: Record<string, any>
  ): Promise<DesktopResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : undefined,
      });

      if (!response.ok) {
        return { success: false, error: `HTTP ${response.status}` };
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return { success: false, error: (error as Error).message };
    }
  }

  private getEndpointPrefix(): string {
    return `/com/${this.software}`;
  }

  /**
   * Connect to CAD software
   */
  async connect(software: CADSoftware = "solidworks"): Promise<boolean> {
    this.software = software;
    const result = await this.fetch(`${this.getEndpointPrefix()}/connect`);
    return result.success;
  }

  /**
   * Create a new part document
   */
  async newPart(): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/new_part`);
    return result.success;
  }

  /**
   * Create a sketch on a plane
   */
  async createSketch(plane: string = "Front"): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/create_sketch`, "POST", {
      plane,
    });
    return result.success;
  }

  /**
   * Draw a circle
   */
  async drawCircle(x: number, y: number, radius: number): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/draw_circle`, "POST", {
      x,
      y,
      radius,
    });
    return result.success;
  }

  /**
   * Draw a rectangle
   */
  async drawRectangle(
    x1: number,
    y1: number,
    x2: number,
    y2: number
  ): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/draw_rectangle`, "POST", {
      x1,
      y1,
      x2,
      y2,
    });
    return result.success;
  }

  /**
   * Draw a line
   */
  async drawLine(
    x1: number,
    y1: number,
    x2: number,
    y2: number
  ): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/draw_line`, "POST", {
      x1,
      y1,
      x2,
      y2,
    });
    return result.success;
  }

  /**
   * Extrude the current sketch
   */
  async extrude(depth: number): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/extrude`, "POST", {
      depth,
    });
    return result.success;
  }

  /**
   * Revolve the current sketch
   */
  async revolve(angle: number = 360): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/revolve`, "POST", {
      angle,
    });
    return result.success;
  }

  /**
   * Create a circular pattern
   */
  async circularPattern(count: number, angle: number = 360): Promise<boolean> {
    const result = await this.fetch(
      `${this.getEndpointPrefix()}/pattern_circular`,
      "POST",
      { count, angle }
    );
    return result.success;
  }

  /**
   * Create a linear pattern
   */
  async linearPattern(
    countX: number,
    countY: number,
    spacingX: number,
    spacingY: number
  ): Promise<boolean> {
    const result = await this.fetch(
      `${this.getEndpointPrefix()}/pattern_linear`,
      "POST",
      { count_x: countX, count_y: countY, spacing_x: spacingX, spacing_y: spacingY }
    );
    return result.success;
  }

  /**
   * Add a fillet
   */
  async fillet(radius: number): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/fillet`, "POST", {
      radius,
    });
    return result.success;
  }

  /**
   * Add a chamfer
   */
  async chamfer(distance: number): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/chamfer`, "POST", {
      distance,
    });
    return result.success;
  }

  /**
   * Save the document
   */
  async save(filepath: string): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/save`, "POST", {
      filepath,
    });
    return result.success;
  }

  /**
   * Take a screenshot
   */
  async takeScreenshot(): Promise<string | undefined> {
    const result = await this.fetch<{ image: string }>("/screen/screenshot", "POST");
    return result.data?.image;
  }

  /**
   * Close the document without saving
   */
  async close(): Promise<boolean> {
    const result = await this.fetch(`${this.getEndpointPrefix()}/close`, "POST");
    return result.success;
  }
}
