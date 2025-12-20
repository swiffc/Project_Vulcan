import { createCipheriv, createDecipheriv, randomBytes, scryptSync } from "crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { dirname } from "path";
import type { TokenInfo, J2SessionStatus } from "./types";

// Token storage file path from environment or default
const TOKEN_STORE_PATH = process.env.TOKEN_STORE_PATH || "./data/tokens.enc";
const ENCRYPTION_KEY = process.env.TOKEN_ENCRYPTION_KEY || "default-key-change-in-production-32";

// AES-256-GCM encryption
const ALGORITHM = "aes-256-gcm";
const IV_LENGTH = 16;
const AUTH_TAG_LENGTH = 16;

interface TokenStore {
  microsoft?: TokenInfo;
  j2?: {
    cookies: string;
    expiresAt: number;
  };
  updatedAt: string;
}

// Derive a 32-byte key from the encryption key
function getKey(): Buffer {
  return scryptSync(ENCRYPTION_KEY, "vulcan-salt", 32);
}

// Encrypt data
function encrypt(data: string): string {
  const iv = randomBytes(IV_LENGTH);
  const key = getKey();
  const cipher = createCipheriv(ALGORITHM, key, iv);

  let encrypted = cipher.update(data, "utf8", "hex");
  encrypted += cipher.final("hex");

  const authTag = cipher.getAuthTag();

  // Format: iv:authTag:encryptedData
  return `${iv.toString("hex")}:${authTag.toString("hex")}:${encrypted}`;
}

// Decrypt data
function decrypt(encryptedData: string): string {
  const parts = encryptedData.split(":");
  if (parts.length !== 3) {
    throw new Error("Invalid encrypted data format");
  }

  const iv = Buffer.from(parts[0], "hex");
  const authTag = Buffer.from(parts[1], "hex");
  const encrypted = parts[2];

  const key = getKey();
  const decipher = createDecipheriv(ALGORITHM, key, iv);
  decipher.setAuthTag(authTag);

  let decrypted = decipher.update(encrypted, "hex", "utf8");
  decrypted += decipher.final("utf8");

  return decrypted;
}

// Read token store from disk
function readStore(): TokenStore {
  try {
    if (!existsSync(TOKEN_STORE_PATH)) {
      return { updatedAt: new Date().toISOString() };
    }

    const encryptedData = readFileSync(TOKEN_STORE_PATH, "utf8");
    const decrypted = decrypt(encryptedData);
    return JSON.parse(decrypted);
  } catch (error) {
    console.error("Failed to read token store:", error);
    return { updatedAt: new Date().toISOString() };
  }
}

// Write token store to disk
function writeStore(store: TokenStore): void {
  try {
    // Ensure directory exists
    const dir = dirname(TOKEN_STORE_PATH);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }

    store.updatedAt = new Date().toISOString();
    const data = JSON.stringify(store);
    const encrypted = encrypt(data);
    writeFileSync(TOKEN_STORE_PATH, encrypted, "utf8");
  } catch (error) {
    console.error("Failed to write token store:", error);
    throw error;
  }
}

// ============= Microsoft Token Management =============

export async function storeMicrosoftToken(token: TokenInfo): Promise<void> {
  const store = readStore();
  store.microsoft = token;
  writeStore(store);
}

export async function getMicrosoftToken(): Promise<TokenInfo | null> {
  const store = readStore();
  return store.microsoft || null;
}

export async function removeMicrosoftToken(): Promise<void> {
  const store = readStore();
  delete store.microsoft;
  writeStore(store);
}

export async function isMicrosoftTokenValid(): Promise<boolean> {
  const token = await getMicrosoftToken();
  if (!token) return false;

  // Check if token expires in less than 5 minutes
  const expiresIn = token.expires_at - Date.now();
  return expiresIn > 5 * 60 * 1000;
}

// ============= J2 Session Management =============

export async function storeJ2Session(cookies: string, expiresAt: number): Promise<void> {
  const store = readStore();
  store.j2 = { cookies, expiresAt };
  writeStore(store);
}

export async function getJ2Session(): Promise<{ cookies: string; expiresAt: number } | null> {
  const store = readStore();
  return store.j2 || null;
}

export async function removeJ2Session(): Promise<void> {
  const store = readStore();
  delete store.j2;
  writeStore(store);
}

export async function isJ2SessionValid(): Promise<boolean> {
  const session = await getJ2Session();
  if (!session) return false;

  // Check if session expires in less than 10 minutes
  const expiresIn = session.expiresAt - Date.now();
  return expiresIn > 10 * 60 * 1000;
}

export async function getJ2SessionStatus(): Promise<J2SessionStatus> {
  const session = await getJ2Session();
  if (!session) {
    return { isAuthenticated: false };
  }

  const isValid = await isJ2SessionValid();
  return {
    isAuthenticated: isValid,
    expiresAt: session.expiresAt,
    lastRefresh: undefined, // Could track this separately
  };
}

// ============= General Token Management =============

export async function clearAllTokens(): Promise<void> {
  writeStore({ updatedAt: new Date().toISOString() });
}

export async function getTokenStoreInfo(): Promise<{
  hasMicrosoft: boolean;
  hasJ2: boolean;
  updatedAt: string;
}> {
  const store = readStore();
  return {
    hasMicrosoft: !!store.microsoft,
    hasJ2: !!store.j2,
    updatedAt: store.updatedAt,
  };
}
