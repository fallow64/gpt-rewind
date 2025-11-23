"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";

export default function EasiestQuestionSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  const easiestQuestion = data.easiestQuestion || "be helpful";

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950 p-12">
      <div className="w-full max-w-4xl space-y-12 text-center">
        {/* Header */}
        <div className="space-y-4">
          <h2 className="text-5xl font-bold text-white">
            Your Easiest Question
          </h2>
          <p className="text-2xl text-white/90">We all start somewhere...</p>
        </div>

        {/* Question display */}
        <div className="bg-white/10 backdrop-blur-sm rounded-3xl p-12 border border-white/20 shadow-2xl">
          <div className="space-y-6">
            <div className="text-6xl">🤔</div>
            <div className="text-4xl font-bold text-white/95 leading-relaxed">
              "How to:{" "}
              <span className="text-purple-300">{easiestQuestion}</span>"
            </div>
          </div>
        </div>

        {/* Fun commentary */}
        <div className="space-y-4">
          <p className="text-xl text-white/80 italic">
            Hey, no judgment! Everyone asks simple questions sometimes.
          </p>
          <p className="text-lg text-white/70">
            The important thing is you're learning! 📚
          </p>
        </div>
      </div>
    </div>
  );
}
