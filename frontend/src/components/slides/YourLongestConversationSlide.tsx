"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";

export default function YourLongestConversationSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  const longestConversationHours = data.longestConversationHours || 0;

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950 p-12">
      <div className="w-full max-w-4xl space-y-12 text-center">
        {/* Header */}
        <div className="space-y-4">
          <h2 className="text-5xl font-bold text-white">
            Your Longest Conversation
          </h2>
          <p className="text-2xl text-white/90">The marathon chat session</p>
        </div>

        {/* Main stat */}
        <div className="space-y-6">
          <div className="inline-block">
            <div className="text-9xl font-black text-white drop-shadow-2xl">
              {longestConversationHours.toFixed(1)}
            </div>
            <div className="text-4xl font-semibold text-white/90 mt-2">
              hours
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
