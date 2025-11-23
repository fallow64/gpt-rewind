"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";

export default function EstimatedProfessionSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  const estimatedProfession = data.estimatedProfession || "Professional";

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950 p-12">
      <div className="w-full max-w-4xl space-y-12 text-center">
        {/* Header */}
        <div className="space-y-4">
          <h2 className="text-5xl font-bold text-white">You Seem Like A...</h2>
          <p className="text-2xl text-white/90">
            Based on your conversations...
          </p>
        </div>

        {/* Profession display */}
        <div className="bg-white/10 backdrop-blur-sm rounded-3xl p-16 border border-white/20 shadow-2xl">
          <div className="space-y-8">
            <div className="text-8xl">👔</div>
            <div className="text-6xl font-black text-transparent bg-linear-to-r from-cyan-300 via-blue-300 to-purple-300 bg-clip-text">
              {estimatedProfession}
            </div>
          </div>
        </div>

        {/* Fun commentary */}
        <div className="space-y-4">
          <p className="text-xl text-white/80 italic">
            Your questions tell a story!
          </p>
          <p className="text-lg text-white/70">
            This is based on patterns in your GPT conversations
          </p>
        </div>

        {/* Disclaimer */}
        <div className="text-sm text-white/50 italic">
          (Just an educated guess - we might be totally wrong! 😄)
        </div>
      </div>
    </div>
  );
}
