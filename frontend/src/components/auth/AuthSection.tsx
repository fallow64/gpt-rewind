"use client";

import { useSession, signIn, signOut } from "next-auth/react";
import Image from "next/image";

function AuthSection() {
  const { data: session, status } = useSession();

  if (session) {
    // if user logged in
    return (
      <div className="flex items-center gap-4">
        <div className="text-sm text-right">
          <div className="text-white/90">{session.user?.name}</div>
          <div className="text-xs text-white/60">{session.user?.email}</div>
        </div>
        <button
          onClick={() => signOut()}
          className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
        >
          Sign Out
        </button>
      </div>
    );
  }

  // Show buttons while loading to prevent flash, disable interaction
  const isLoading = status === "loading";

  return (
    <div
      className={`flex gap-2 ${
        isLoading ? "opacity-50 pointer-events-none" : ""
      }`}
    >
      <button
        onClick={() => !isLoading && signIn("google")}
        disabled={isLoading}
        className="px-4 py-2 text-sm bg-white hover:bg-gray-100 text-gray-900 font-semibold rounded-lg transition-colors flex items-center gap-2"
      >
        <Image
          src="/google-icon.svg"
          alt="Google"
          width={16}
          height={16}
          className="w-4 h-4"
        />
        Google
      </button>
      <button
        onClick={() => !isLoading && signIn("discord")}
        disabled={isLoading}
        className="px-4 py-2 text-sm bg-[#5865F2] hover:bg-[#4752C4] text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
      >
        <Image
          src="/discord-icon.svg"
          alt="Discord"
          width={16}
          height={16}
          className="w-4 h-4"
        />
        Discord
      </button>
    </div>
  );
}

export default AuthSection;
