import { PublicClientApplication, DeviceCodeRequest, AuthenticationResult } from "@azure/msal-node";
import { storeMicrosoftToken, getMicrosoftToken, removeMicrosoftToken } from "./token-manager";
import type { TokenInfo, DeviceCodeResponse, Email, TeamsChat, TeamsMention, DriveFile } from "./types";

// Azure CLI's public client ID (works without app registration)
const CLIENT_ID = process.env.MICROSOFT_CLIENT_ID || "04b07795-8ddb-461a-bbee-02f9e1bf7b46";
const TENANT_ID = process.env.MICROSOFT_TENANT_ID || "common";
const AUTHORITY = `https://login.microsoftonline.com/${TENANT_ID}`;

// Microsoft Graph scopes
const SCOPES = [
  "User.Read",
  "Mail.Read",
  "Chat.Read",
  "Files.Read",
  "offline_access",
];

// MSAL configuration
const msalConfig = {
  auth: {
    clientId: CLIENT_ID,
    authority: AUTHORITY,
  },
};

// Create MSAL instance
let msalClient: PublicClientApplication | null = null;

function getMsalClient(): PublicClientApplication {
  if (!msalClient) {
    msalClient = new PublicClientApplication(msalConfig);
  }
  return msalClient;
}

// Store for pending device code requests
const pendingDeviceCodes = new Map<string, {
  deviceCode: string;
  expiresAt: number;
  interval: number;
}>();

// ============= Device Code Flow =============

export interface DeviceCodeResult {
  userCode: string;
  verificationUri: string;
  message: string;
  expiresIn: number;
  requestId: string;
}

export async function initiateDeviceCodeFlow(): Promise<DeviceCodeResult> {
  const client = getMsalClient();

  return new Promise((resolve, reject) => {
    const requestId = Math.random().toString(36).substring(7);

    const request: DeviceCodeRequest = {
      scopes: SCOPES,
      deviceCodeCallback: (response) => {
        // Store the device code for later polling
        pendingDeviceCodes.set(requestId, {
          deviceCode: response.deviceCode,
          expiresAt: Date.now() + response.expiresIn * 1000,
          interval: response.interval * 1000,
        });

        resolve({
          userCode: response.userCode,
          verificationUri: response.verificationUri,
          message: response.message,
          expiresIn: response.expiresIn,
          requestId,
        });
      },
    };

    // Start the device code flow
    client.acquireTokenByDeviceCode(request)
      .then(async (result) => {
        if (result) {
          // Token acquired! Store it
          await storeAuthResult(result);
          pendingDeviceCodes.delete(requestId);
        }
      })
      .catch((error) => {
        pendingDeviceCodes.delete(requestId);
        // Don't reject here - the device code callback already resolved
        console.error("Device code flow error:", error);
      });
  });
}

// Store authentication result
async function storeAuthResult(result: AuthenticationResult): Promise<void> {
  const tokenInfo: TokenInfo = {
    access_token: result.accessToken,
    refresh_token: result.account?.homeAccountId || "", // MSAL handles refresh internally
    expires_at: result.expiresOn?.getTime() || Date.now() + 3600000,
    scope: result.scopes.join(" "),
  };

  await storeMicrosoftToken(tokenInfo);
}

// Check if device code has been authorized
export async function checkDeviceCodeStatus(requestId: string): Promise<{
  status: "pending" | "authorized" | "expired" | "error";
  message?: string;
}> {
  const pending = pendingDeviceCodes.get(requestId);

  if (!pending) {
    // Check if we now have a valid token (user completed auth)
    const token = await getMicrosoftToken();
    if (token && token.expires_at > Date.now()) {
      return { status: "authorized" };
    }
    return { status: "expired", message: "Device code request not found or expired" };
  }

  if (Date.now() > pending.expiresAt) {
    pendingDeviceCodes.delete(requestId);
    return { status: "expired", message: "Device code expired" };
  }

  // Still waiting for user to authorize
  return { status: "pending" };
}

// ============= Token Management =============

export async function getAccessToken(): Promise<string | null> {
  const token = await getMicrosoftToken();
  if (!token) return null;

  // Check if token is expired
  if (token.expires_at < Date.now()) {
    // Try to refresh using MSAL's cache
    try {
      const client = getMsalClient();
      const accounts = await client.getTokenCache().getAllAccounts();

      if (accounts.length > 0) {
        const result = await client.acquireTokenSilent({
          account: accounts[0],
          scopes: SCOPES,
        });

        if (result) {
          await storeAuthResult(result);
          return result.accessToken;
        }
      }
    } catch (error) {
      console.error("Token refresh failed:", error);
      await removeMicrosoftToken();
      return null;
    }
  }

  return token.access_token;
}

export async function signOut(): Promise<void> {
  await removeMicrosoftToken();
  msalClient = null;
}

// ============= Graph API Calls =============

const GRAPH_BASE = "https://graph.microsoft.com/v1.0";

async function graphRequest<T>(endpoint: string): Promise<T | null> {
  const token = await getAccessToken();
  if (!token) return null;

  const response = await fetch(`${GRAPH_BASE}${endpoint}`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    console.error(`Graph API error: ${response.status} ${response.statusText}`);
    return null;
  }

  return response.json();
}

// Get current user info
export async function getCurrentUser(): Promise<{ email: string; name: string } | null> {
  const result = await graphRequest<{
    mail?: string;
    userPrincipalName: string;
    displayName: string;
  }>("/me");

  if (!result) return null;

  return {
    email: result.mail || result.userPrincipalName,
    name: result.displayName,
  };
}

// ============= Email API =============

interface GraphMessage {
  id: string;
  subject: string;
  from: {
    emailAddress: {
      name: string;
      address: string;
    };
  };
  receivedDateTime: string;
  isRead: boolean;
  importance: string;
  bodyPreview: string;
  webLink?: string;
}

export async function getEmails(options?: {
  top?: number;
  unreadOnly?: boolean;
}): Promise<Email[]> {
  const top = options?.top || 20;
  let filter = "";

  if (options?.unreadOnly) {
    filter = "&$filter=isRead eq false";
  }

  const result = await graphRequest<{ value: GraphMessage[] }>(
    `/me/messages?$top=${top}&$orderby=receivedDateTime desc&$select=id,subject,from,receivedDateTime,isRead,importance,bodyPreview,webLink${filter}`
  );

  if (!result) return [];

  return result.value.map((msg) => ({
    id: msg.id,
    subject: msg.subject || "(No Subject)",
    from: {
      name: msg.from?.emailAddress?.name || "Unknown",
      email: msg.from?.emailAddress?.address || "",
    },
    receivedAt: msg.receivedDateTime,
    isRead: msg.isRead,
    importance: msg.importance.toLowerCase() as "low" | "normal" | "high",
    preview: msg.bodyPreview || "",
    webLink: msg.webLink,
  }));
}

export async function getUnreadCount(): Promise<{ total: number; important: number }> {
  const result = await graphRequest<{ "@odata.count": number }>(
    "/me/messages?$filter=isRead eq false&$count=true&$top=1"
  );

  const importantResult = await graphRequest<{ "@odata.count": number }>(
    "/me/messages?$filter=isRead eq false and importance eq 'high'&$count=true&$top=1"
  );

  return {
    total: result?.["@odata.count"] || 0,
    important: importantResult?.["@odata.count"] || 0,
  };
}

// ============= Teams API =============

interface GraphChat {
  id: string;
  topic: string;
  chatType: string;
  lastUpdatedDateTime: string;
  webUrl?: string;
}

interface GraphChatMessage {
  id: string;
  body: { content: string };
  from: {
    user?: { displayName: string };
  };
  createdDateTime: string;
}

export async function getTeamsChats(top = 10): Promise<TeamsChat[]> {
  const result = await graphRequest<{ value: GraphChat[] }>(
    `/me/chats?$top=${top}&$orderby=lastUpdatedDateTime desc`
  );

  if (!result) return [];

  const chats: TeamsChat[] = [];

  for (const chat of result.value) {
    // Get last message for each chat
    const messages = await graphRequest<{ value: GraphChatMessage[] }>(
      `/me/chats/${chat.id}/messages?$top=1&$orderby=createdDateTime desc`
    );

    const lastMsg = messages?.value?.[0];

    chats.push({
      id: chat.id,
      topic: chat.topic || "Chat",
      type: chat.chatType === "group" ? "group" : "oneOnOne",
      lastMessage: {
        content: lastMsg?.body?.content?.replace(/<[^>]*>/g, "") || "",
        from: lastMsg?.from?.user?.displayName || "Unknown",
        timestamp: lastMsg?.createdDateTime || chat.lastUpdatedDateTime,
      },
      unreadCount: 0, // Graph API doesn't provide this directly
      webUrl: chat.webUrl,
    });
  }

  return chats;
}

export async function getTeamsMentions(): Promise<TeamsMention[]> {
  // Note: Getting mentions requires specific permissions and filtering
  // This is a simplified implementation
  const result = await graphRequest<{ value: GraphChatMessage[] }>(
    "/me/chats/messages?$top=50&$orderby=createdDateTime desc"
  );

  if (!result) return [];

  // Filter for messages that might contain mentions (simplified)
  return result.value
    .filter((msg) => msg.body?.content?.includes("@"))
    .slice(0, 5)
    .map((msg) => ({
      chatId: "",
      messageId: msg.id,
      mentionedBy: msg.from?.user?.displayName || "Unknown",
      preview: msg.body?.content?.replace(/<[^>]*>/g, "").substring(0, 100) || "",
      timestamp: msg.createdDateTime,
    }));
}

// ============= Files API =============

interface GraphDriveItem {
  id: string;
  name: string;
  webUrl: string;
  lastModifiedDateTime: string;
  lastModifiedBy?: {
    user?: { displayName: string };
  };
  size: number;
  file?: { mimeType: string };
  parentReference?: { path: string };
}

export async function getRecentFiles(top = 10): Promise<DriveFile[]> {
  const result = await graphRequest<{ value: GraphDriveItem[] }>(
    `/me/drive/recent?$top=${top}`
  );

  if (!result) return [];

  return result.value
    .filter((item) => item.file) // Only files, not folders
    .map((item) => ({
      id: item.id,
      name: item.name,
      path: item.parentReference?.path?.replace("/drive/root:", "") || "/",
      webUrl: item.webUrl,
      lastModified: item.lastModifiedDateTime,
      modifiedBy: item.lastModifiedBy?.user?.displayName || "Unknown",
      size: item.size,
      mimeType: item.file?.mimeType || "application/octet-stream",
    }));
}

export async function searchFiles(query: string, top = 10): Promise<DriveFile[]> {
  const result = await graphRequest<{ value: GraphDriveItem[] }>(
    `/me/drive/root/search(q='${encodeURIComponent(query)}')?$top=${top}`
  );

  if (!result) return [];

  return result.value
    .filter((item) => item.file)
    .map((item) => ({
      id: item.id,
      name: item.name,
      path: item.parentReference?.path?.replace("/drive/root:", "") || "/",
      webUrl: item.webUrl,
      lastModified: item.lastModifiedDateTime,
      modifiedBy: item.lastModifiedBy?.user?.displayName || "Unknown",
      size: item.size,
      mimeType: item.file?.mimeType || "application/octet-stream",
    }));
}
