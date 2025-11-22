# Authentication Setup

This project uses NextAuth.js v5 (Auth.js) for authentication with Google and Discord OAuth providers.

## Setup Instructions

### 1. Copy the environment variables

```bash
cp .env.example .env.local
```

### 2. Generate an AUTH_SECRET

```bash
openssl rand -base64 32
```

Copy the output and paste it as the `AUTH_SECRET` value in `.env.local`.

### 3. Set up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project (or select an existing one)
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Select "Web application"
6. Add authorized redirect URIs:
   - For development: `http://localhost:3000/api/auth/callback/google`
   - For production: `https://yourdomain.com/api/auth/callback/google`
7. Copy the Client ID and Client Secret to your `.env.local` file

### 4. Set up Discord OAuth

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" (or select an existing one)
3. Go to "OAuth2" in the left sidebar
4. Copy the Client ID and Client Secret
5. Add redirect URIs:
   - For development: `http://localhost:3000/api/auth/callback/discord`
   - For production: `https://yourdomain.com/api/auth/callback/discord`
6. Paste the Client ID and Client Secret to your `.env.local` file

### 5. Your `.env.local` should look like:

```env
AUTH_SECRET=your-generated-secret-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
DISCORD_CLIENT_ID=your-discord-client-id
DISCORD_CLIENT_SECRET=your-discord-client-secret
```

## Usage

### Using the LoginButton Component

```tsx
import LoginButton from "@/components/auth/LoginButton";

export default function Page() {
  return (
    <div>
      <LoginButton />
    </div>
  );
}
```

### Accessing the User Session

```tsx
"use client";

import { useSession } from "next-auth/react";

export default function MyComponent() {
  const { data: session } = useSession();

  if (session) {
    console.log("User ID:", session.user.id); // Unique user ID
    console.log("Email:", session.user.email);
    console.log("Name:", session.user.name);
  }

  return <div>...</div>;
}
```

### Server-side Session Access

```tsx
import { auth } from "@/auth";

export default async function Page() {
  const session = await auth();

  if (session) {
    console.log("User ID:", session.user.id); // Unique user ID
  }

  return <div>...</div>;
}
```

## Features

- ✅ Google OAuth login
- ✅ Discord OAuth login
- ✅ Unique user ID (`session.user.id`) for each authenticated user
- ✅ Beautiful UI with provider-specific branding
- ✅ Sign out functionality
- ✅ Loading states
- ✅ Session persistence across page reloads

## Notes

- The `session.user.id` is a unique identifier derived from the OAuth provider's user ID
- Sessions are stored server-side and secured with the AUTH_SECRET
- The LoginButton component automatically handles sign-in and sign-out states
