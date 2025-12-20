"use client";

import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import Link from "next/link";

export default function WorkSetupPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8">
        <Link href="/work" className="text-vulcan-accent hover:underline text-sm">
          &larr; Back to Work Hub
        </Link>
      </div>

      <h1 className="text-3xl font-bold text-white mb-2">Microsoft 365 Setup</h1>
      <p className="text-white/50 mb-8">
        Create a free Azure AD app registration to connect your Microsoft 365 account.
        No admin approval required.
      </p>

      <div className="space-y-6">
        {/* Step 1 */}
        <Card>
          <CardHeader
            title="Step 1: Open Azure Portal"
            subtitle="Go to App registrations"
          />
          <CardContent>
            <p className="text-white/60 mb-4">
              Sign in with your Microsoft 365 account (the same one you use for Outlook/Teams).
            </p>
            <Button
              variant="primary"
              onClick={() => window.open("https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade", "_blank")}
            >
              Open Azure App Registrations
            </Button>
          </CardContent>
        </Card>

        {/* Step 2 */}
        <Card>
          <CardHeader
            title="Step 2: Create New Registration"
            subtitle="Click 'New registration'"
          />
          <CardContent>
            <div className="space-y-4 text-white/60">
              <div className="bg-white/5 rounded-lg p-4 space-y-2">
                <p><strong className="text-white">Name:</strong> Project Vulcan</p>
                <p><strong className="text-white">Supported account types:</strong> Accounts in any organizational directory and personal Microsoft accounts</p>
                <p><strong className="text-white">Redirect URI:</strong> Leave blank (not needed for Device Code Flow)</p>
              </div>
              <p>Click <strong className="text-white">Register</strong></p>
            </div>
          </CardContent>
        </Card>

        {/* Step 3 */}
        <Card>
          <CardHeader
            title="Step 3: Enable Public Client"
            subtitle="Allow Device Code Flow"
          />
          <CardContent>
            <ol className="space-y-2 text-white/60 list-decimal list-inside">
              <li>In your new app, go to <strong className="text-white">Authentication</strong> in the left menu</li>
              <li>Scroll to <strong className="text-white">Advanced settings</strong></li>
              <li>Set <strong className="text-white">"Allow public client flows"</strong> to <strong className="text-green-400">Yes</strong></li>
              <li>Click <strong className="text-white">Save</strong></li>
            </ol>
          </CardContent>
        </Card>

        {/* Step 4 */}
        <Card>
          <CardHeader
            title="Step 4: Add API Permissions"
            subtitle="Grant access to Mail, Teams, Files"
          />
          <CardContent>
            <ol className="space-y-2 text-white/60 list-decimal list-inside mb-4">
              <li>Go to <strong className="text-white">API permissions</strong> in the left menu</li>
              <li>Click <strong className="text-white">Add a permission</strong></li>
              <li>Select <strong className="text-white">Microsoft Graph</strong></li>
              <li>Select <strong className="text-white">Delegated permissions</strong></li>
              <li>Search and add these permissions:</li>
            </ol>
            <div className="bg-white/5 rounded-lg p-4 font-mono text-sm space-y-1">
              <p className="text-green-400">User.Read</p>
              <p className="text-blue-400">Mail.Read</p>
              <p className="text-purple-400">Chat.Read</p>
              <p className="text-amber-400">Files.Read</p>
              <p className="text-white/40">offline_access</p>
            </div>
            <p className="text-white/40 text-sm mt-4">
              These are "delegated" permissions - they only access what YOU can access, not admin-level data.
            </p>
          </CardContent>
        </Card>

        {/* Step 5 */}
        <Card>
          <CardHeader
            title="Step 5: Copy Your Client ID"
            subtitle="Get the Application (client) ID"
          />
          <CardContent>
            <ol className="space-y-2 text-white/60 list-decimal list-inside mb-4">
              <li>Go to <strong className="text-white">Overview</strong> in the left menu</li>
              <li>Copy the <strong className="text-white">Application (client) ID</strong></li>
              <li>It looks like: <code className="bg-white/10 px-2 py-1 rounded">xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx</code></li>
            </ol>
          </CardContent>
        </Card>

        {/* Step 6 */}
        <Card>
          <CardHeader
            title="Step 6: Add to Environment Variables"
            subtitle="Configure Project Vulcan"
          />
          <CardContent>
            <p className="text-white/60 mb-4">
              Add these to your <code className="bg-white/10 px-2 py-1 rounded">.env.local</code> file:
            </p>
            <div className="bg-vulcan-dark rounded-lg p-4 font-mono text-sm">
              <p className="text-white/40"># Microsoft Graph API</p>
              <p><span className="text-green-400">MICROSOFT_CLIENT_ID</span>=<span className="text-amber-400">your-client-id-here</span></p>
              <p><span className="text-green-400">MICROSOFT_TENANT_ID</span>=<span className="text-amber-400">common</span></p>
            </div>
            <p className="text-white/40 text-sm mt-4">
              Then restart the dev server and try connecting again.
            </p>
          </CardContent>
        </Card>

        {/* Back Button */}
        <div className="flex justify-center pt-4">
          <Link href="/work">
            <Button variant="primary" size="lg">
              Done - Back to Work Hub
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
