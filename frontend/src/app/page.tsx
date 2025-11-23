"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useConversation } from "@/src/contexts/ConversationContext";
import UploadStep from "@/src/components/UploadStep";

export default function Home() {
  const router = useRouter();
  const { setConversationId } = useConversation();
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== "application/json") {
      alert("Please upload a valid JSON file");
      return;
    }

    setIsUploading(true);

    try {
      // Create FormData to upload the file
      const formData = new FormData();
      formData.append("file", file);

      // Upload to backend
      const response = await fetch("http://localhost:8000/conversation", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload conversation data");
      }

      const result = await response.json();
      const conversationId = result.conversationId;

      if (!conversationId) {
        throw new Error("No conversation ID returned from server");
      }

      // Store conversation ID in context
      setConversationId(conversationId);

      // Redirect to insights
      router.push("/insights");
    } catch (error) {
      console.error("Error processing data:", error);
      alert("Failed to process data. Please try again.");
      setIsUploading(false);
    }
  };

  return (
    <div
      className="flex flex-col items-center justify-center bg-linear-to-br from-gray-950 via-gray-900 to-black text-white p-8"
      style={{ minHeight: "calc(100vh - 64px)" }}
    >
      <div className="max-w-4xl mx-auto w-full space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-6xl font-bold">Welcome to GPT Rewind</h1>
          <p className="text-2xl text-white/80">
            Discover your ChatGPT conversation insights
          </p>
        </div>

        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 min-h-[300px] flex flex-col items-center justify-center">
          <UploadStep
            onFileUpload={handleFileUpload}
            isUploading={isUploading}
          />
        </div>
      </div>
    </div>
  );
}
