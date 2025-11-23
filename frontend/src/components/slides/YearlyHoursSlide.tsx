"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";

export default function YearlyHoursSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  const totalHours = data.totalHours || 0;

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-12 bg-linear-to-br from-blue-600 via-cyan-600 to-teal-600">
      <div className="text-center space-y-8">
        <h2 className="text-6xl font-bold text-white mb-8">
          Time Spent with GPT
        </h2>

        <div className="space-y-4">
          <p className="text-8xl font-black text-white drop-shadow-2xl">
            {totalHours.toFixed(1)}
          </p>
          <p className="text-5xl font-bold text-white/90">hours</p>
        </div>

        <p className="text-3xl font-semibold text-white/95 mt-12 max-w-3xl">
          You have spent {totalHours.toFixed(1)} hours conversing with GPT
        </p>

        <div className="mt-8 text-xl text-white/80">
          That's {Math.floor(totalHours / 24)} days and{" "}
          {Math.floor(totalHours % 24)} hours!
        </div>
      </div>
    </div>
  );
}
