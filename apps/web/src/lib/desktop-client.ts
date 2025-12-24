/**
 * Desktop Server Client
 *
 * Proxy client for communicating with the Desktop Control Server.
 * All physical PC control goes through this client.
 */

const DESKTOP_SERVER_URL =
  process.env.DESKTOP_SERVER_URL || "http://localhost:8000";

interface DesktopResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

async function desktopFetch<T>(
  endpoint: string,
  method: "GET" | "POST" = "POST",
  body?: Record<string, any>
): Promise<DesktopResponse<T>> {
  try {
    const response = await fetch(`${DESKTOP_SERVER_URL}${endpoint}`, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      return {
        success: false,
        error: `Desktop server error: ${response.status}`,
      };
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: `Desktop server unreachable: ${(error as Error).message}`,
    };
  }
}

// Mouse control
export const mouse = {
  move: (x: number, y: number, duration?: number) =>
    desktopFetch("/mouse/move", "POST", { x, y, duration }),

  click: (x?: number, y?: number, button?: "left" | "right" | "middle") =>
    desktopFetch("/mouse/click", "POST", { x, y, button }),

  drag: (x1: number, y1: number, x2: number, y2: number) =>
    desktopFetch("/mouse/drag", "POST", { x1, y1, x2, y2 }),

  scroll: (clicks: number, x?: number, y?: number) =>
    desktopFetch("/mouse/scroll", "POST", { clicks, x, y }),
};

// Keyboard control
export const keyboard = {
  type: (text: string, interval?: number) =>
    desktopFetch("/keyboard/type", "POST", { text, interval }),

  press: (key: string) =>
    desktopFetch("/keyboard/press", "POST", { key }),

  hotkey: (keys: string[]) =>
    desktopFetch("/keyboard/hotkey", "POST", { keys }),
};

// Screen control
export const screen = {
  screenshot: () =>
    desktopFetch<{ image: string }>("/screen/screenshot", "POST"),

  region: (x: number, y: number, width: number, height: number) =>
    desktopFetch<{ image: string }>("/screen/region", "POST", {
      x,
      y,
      width,
      height,
    }),

  ocr: (x?: number, y?: number, width?: number, height?: number) =>
    desktopFetch<{ text: string }>("/screen/ocr", "POST", {
      x,
      y,
      width,
      height,
    }),
};

// Window control
export const window = {
  list: () =>
    desktopFetch<Array<{ title: string; handle: number }>>(
      "/window/list",
      "GET"
    ),

  focus: (title: string) =>
    desktopFetch("/window/focus", "POST", { title }),

  minimize: (title: string) =>
    desktopFetch("/window/minimize", "POST", { title }),

  maximize: (title: string) =>
    desktopFetch("/window/maximize", "POST", { title }),
};

// System control
export const system = {
  health: () => desktopFetch<{ status: string }>("/health", "GET"),

  kill: () => desktopFetch("/kill", "POST"),

  resume: () => desktopFetch("/resume", "POST"),
};

// CAD control (SolidWorks)
export const solidworks = {
  status: () =>
    desktopFetch<{
      connected: boolean;
      version: string;
      has_document: boolean;
      document_name: string | null;
    }>("/com/solidworks/status", "GET"),

  connect: () => desktopFetch("/com/solidworks/connect", "POST"),

  newPart: () => desktopFetch("/com/solidworks/new_part", "POST"),

  createSketch: (plane: string = "Front") =>
    desktopFetch("/com/solidworks/create_sketch", "POST", { plane }),

  drawCircle: (x: number, y: number, radius: number) =>
    desktopFetch("/com/solidworks/draw_circle", "POST", { x, y, radius }),

  drawRectangle: (x1: number, y1: number, x2: number, y2: number) =>
    desktopFetch("/com/solidworks/draw_rectangle", "POST", { x1, y1, x2, y2 }),

  extrude: (depth: number) =>
    desktopFetch("/com/solidworks/extrude", "POST", { depth }),

  save: (filepath: string) =>
    desktopFetch("/com/solidworks/save", "POST", { filepath }),
};

// CAD control (Inventor)
export const inventor = {
  connect: () => desktopFetch("/com/inventor/connect", "POST"),

  newPart: () => desktopFetch("/com/inventor/new_part", "POST"),

  createSketch: (plane: string = "XY") =>
    desktopFetch("/com/inventor/create_sketch", "POST", { plane }),

  drawCircle: (x: number, y: number, radius: number) =>
    desktopFetch("/com/inventor/draw_circle", "POST", { x, y, radius }),

  extrude: (depth: number) =>
    desktopFetch("/com/inventor/extrude", "POST", { depth }),

  save: (filepath: string) =>
    desktopFetch("/com/inventor/save", "POST", { filepath }),
};
