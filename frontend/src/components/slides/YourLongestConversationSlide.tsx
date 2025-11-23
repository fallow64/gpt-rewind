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

        {/* Fun fact */}
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
          <p className="text-xl text-white/95 leading-relaxed">
            {longestConversationHours >= 5 ? (
              <>
                That's like binge-watching{" "}
                <span className="font-bold">
                  {Math.floor(longestConversationHours / 2.5)}
                </span>{" "}
                movies back-to-back!
              </>
            ) : longestConversationHours >= 2 ? (
              <>
                That's longer than most meetings! You were really deep in
                thought.
              </>
            ) : (
              <>Short but meaningful conversations can be the most impactful!</>
            )}
          </p>
        </div>

        {/* Icon decoration */}
        <div className="text-7xl opacity-80">💬</div>
      </div>
    </div>
  );
}
