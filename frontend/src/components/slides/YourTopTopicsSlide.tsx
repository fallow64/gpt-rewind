"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";

export default function YourTopTopicsSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  const topTopics = data;

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950 p-12">
      <div className="w-full max-w-6xl space-y-10 text-center">
        {/* Header */}
        <div className="space-y-4">
          <h2 className="text-6xl font-black text-white tracking-tight">
            Your Top Topics
          </h2>
          <p className="text-2xl text-white/90 font-light">
            The subjects that defined your year
          </p>
          <div className="h-1 w-32 bg-linear-to-r from-transparent via-white/50 to-transparent mx-auto"></div>
        </div>

        {/* Podium */}
        <div className="flex items-end justify-center gap-6 px-8">
          {/* Second Place - Left */}
          <div className="flex flex-col items-center space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-150">
            <div className="text-4xl font-bold text-white/40">2</div>
            <div className="bg-white/10 backdrop-blur-sm border-2 border-white/30 rounded-2xl px-6 py-8 min-w-60 h-[200px] flex items-center justify-center">
              <p className="text-2xl font-semibold text-white/95 leading-tight">
                {topTopics[1]}
              </p>
            </div>
          </div>

          {/* First Place - Center (Tallest) */}
          <div className="flex flex-col items-center space-y-4 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="relative flex items-center justify-center">
              <div className="absolute w-16 h-16 -top-3">
                <div className="w-full h-full bg-linear-to-br from-yellow-300 to-yellow-500 rounded-full animate-crown-pulse"></div>
              </div>
              <div className="text-5xl font-black text-transparent bg-linear-to-r from-yellow-200 via-yellow-300 to-yellow-400 bg-clip-text relative z-10">
                1
              </div>
            </div>
            <div className="bg-linear-to-br from-yellow-500/20 to-orange-500/20 backdrop-blur-sm border-2 border-yellow-400/50 rounded-2xl px-6 py-8 min-w-[260px] h-[260px] flex items-center justify-center shadow-2xl shadow-yellow-500/20">
              <p className="text-3xl font-bold text-white leading-tight">
                {topTopics[0]}
              </p>
            </div>
          </div>

          {/* Third Place - Right */}
          <div className="flex flex-col items-center space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-700 delay-300">
            <div className="text-3xl font-bold text-white/30">3</div>
            <div className="bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-2xl px-6 py-8 min-w-60 h-40 flex items-center justify-center">
              <p className="text-xl font-semibold text-white/90 leading-tight">
                {topTopics[2]}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
