// Work Integration Hub Types

// ============= Microsoft Graph Types =============

export interface DeviceCodeResponse {
  device_code: string;
  user_code: string;
  verification_uri: string;
  expires_in: number;
  interval: number;
  message: string;
}

export interface TokenInfo {
  access_token: string;
  refresh_token: string;
  expires_at: number;
  scope: string;
}

export interface AuthStatus {
  isAuthenticated: boolean;
  expiresAt?: number;
  userEmail?: string;
  error?: string;
}

// ============= Email Types =============

export interface EmailAddress {
  name: string;
  email: string;
}

export interface Email {
  id: string;
  subject: string;
  from: EmailAddress;
  receivedAt: string;
  isRead: boolean;
  importance: "low" | "normal" | "high";
  preview: string;
  webLink?: string;
}

export interface EmailResponse {
  emails: Email[];
  unreadCount: number;
  importantUnread: number;
}

// ============= Teams Types =============

export interface TeamsChat {
  id: string;
  topic: string;
  type: "group" | "oneOnOne";
  lastMessage: {
    content: string;
    from: string;
    timestamp: string;
  };
  unreadCount: number;
  webUrl?: string;
}

export interface TeamsMention {
  chatId: string;
  messageId: string;
  mentionedBy: string;
  preview: string;
  timestamp: string;
}

export interface TeamsResponse {
  chats: TeamsChat[];
  mentions: TeamsMention[];
  totalUnread: number;
}

// ============= Files Types =============

export interface DriveFile {
  id: string;
  name: string;
  path: string;
  webUrl: string;
  lastModified: string;
  modifiedBy: string;
  size: number;
  mimeType: string;
}

export interface FilesResponse {
  files: DriveFile[];
  source: "onedrive" | "sharepoint";
}

// ============= J2 Tracker Types =============

export interface J2Workflow {
  currentStep: string;
  totalSteps: number;
  completedSteps: number;
}

export interface J2Job {
  id: string;
  title: string;
  status: "Pending" | "In Progress" | "Review" | "Complete" | "On Hold";
  assignedTo: string;
  dueDate: string;
  priority: "Low" | "Medium" | "High" | "Critical";
  workflow: J2Workflow;
  webUrl?: string;
}

export interface J2Summary {
  total: number;
  active: number;
  overdue: number;
  dueThisWeek: number;
}

export interface J2Response {
  jobs: J2Job[];
  summary: J2Summary;
  sessionValid: boolean;
}

export interface J2SessionStatus {
  isAuthenticated: boolean;
  lastRefresh?: number;
  expiresAt?: number;
}

// ============= Work Hub Types =============

export interface WorkServiceStatus {
  service: "microsoft" | "j2";
  status: "connected" | "disconnected" | "connecting" | "error";
  lastSync?: string;
  error?: string;
}

export interface WorkHubData {
  emails: EmailResponse | null;
  teams: TeamsResponse | null;
  files: FilesResponse | null;
  j2: J2Response | null;
  services: WorkServiceStatus[];
  lastRefresh: string;
}
