"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";

export default function HardestQuestionSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  const hardestQuestion = data;

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950 p-12">
      <div className="w-full max-w-4xl space-y-12 text-center">
        {/* Header */}
        <div className="space-y-4">
          <h2 className="text-5xl font-bold text-white">
            Your Hardest Question
          </h2>
          <p className="text-2xl text-white/90">When things got serious...</p>
        </div>

        {/* Question display */}
        <div className="bg-linear-to-br from-red-900/20 to-orange-900/20 backdrop-blur-sm rounded-3xl p-12 border border-red-500/30 shadow-2xl">
          <div className="space-y-6">
            <div className="text-6xl">💡</div>
            <div className="text-4xl font-bold text-white/95 leading-relaxed">
              "How to:{" "}
              <span className="text-orange-300">{hardestQuestion}</span>"
            </div>
          </div>
        </div>

        {/* Fun commentary */}
        <div className="space-y-4">
          <p className="text-lg text-white/70">
            You're pushing boundaries and asking the tough questions. Keep it
            up! 🚀
          </p>
        </div>
      </div>
    </div>
  );
}
