# Project Vulcan - Work Hub Setup (Azure AD)

This guide explains how to set up an Azure Active Directory (Azure AD) application to enable the Work Hub functionality in Project Vulcan. This is necessary for the agent to access Microsoft 365 services like Outlook, Calendar, and OneDrive.

## 1. Prerequisites

- An Azure account with an active subscription.
- Permissions to create and manage application registrations in Azure AD.

## 2. Register a New Application

1.  **Navigate to Azure Active Directory:**
    -   Log in to the [Azure portal](https://portal.azure.com).
    -   Search for and select "Azure Active Directory".

2.  **Go to App Registrations:**
    -   In the left-hand menu, select "App registrations".
    -   Click on "New registration".

3.  **Configure the Application:**
    -   **Name:** Enter a name for your application (e.g., "Project Vulcan Work Hub").
    -   **Supported account types:** Select "Accounts in this organizational directory only (Single tenant)".
    -   **Redirect URI (optional):** You can leave this blank for now. We will add it later.
    -   Click "Register".

## 3. Get Application (Client) ID

-   After the application is created, you will be taken to its overview page.
-   Copy the **Application (client) ID**. This is your `MICROSOFT_CLIENT_ID`.
-   Paste this value into your `.env.example` file for the `MICROSOFT_CLIENT_ID` variable.

## 4. Configure Authentication

1.  **Go to Authentication:**
    -   In the left-hand menu, select "Authentication".

2.  **Add a Platform:**
    -   Click on "Add a platform".
    -   Select "Mobile and desktop applications".

3.  **Configure Redirect URIs:**
    -   Under "Redirect URIs", add the following URI:
        -   `http://localhost`
    -   Click "Configure".

4.  **Enable Public Client Flow:**
    -   Scroll down to the "Advanced settings" section.
    -   Set "Allow public client flows" to "Yes".
    -   Click "Save".

## 5. Add API Permissions

1.  **Go to API permissions:**
    -   In the left-hand menu, select "API permissions".

2.  **Add a Permission:**
    -   Click on "Add a permission".
    -   Select "Microsoft Graph".

3.  **Select Delegated Permissions:**
    -   Select "Delegated permissions".
    -   Search for and add the following permissions:
        -   `Calendars.ReadWrite`
        -   `Mail.ReadWrite`
        -   `Files.ReadWrite.All`
        -   `User.Read`
    -   Click "Add permissions".

4.  **Grant Admin Consent (Optional):**
    -   If you are an administrator, you can grant admin consent for the permissions by clicking the "Grant admin consent for [Your Tenant]" button. This will prevent users from having to consent to the permissions individually.

## 6. Configuration in Project Vulcan

1.  **Update `.env.example`:**
    -   Make sure you have added the `MICROSOFT_CLIENT_ID` to your `.env.example` file.
    -   Copy the `.env.example` to a new file named `.env` and fill in the `MICROSOFT_CLIENT_ID` with the value you copied in step 3.

2.  **Run the Desktop Server:**
    -   Start the desktop server as usual.

3.  **Authenticate with Microsoft:**
    -   When you try to use a Work Hub feature for the first time, you will be prompted to authenticate with Microsoft.
    -   A device code will be displayed in the console.
    -   Go to [https://microsoft.com/devicelogin](https://microsoft.com/devicelogin) and enter the code to authenticate.

You have now successfully configured the Azure AD application for Project Vulcan's Work Hub.
