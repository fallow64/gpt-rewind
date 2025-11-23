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
    <div className="w-full h-full flex flex-col items-center justify-between p-12 bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950">
      {/* Top */}
      <div className="text-center pt-4 font-bold">
        <h2 className="text-5xl text-white/90">Time Spent with GPT:</h2>
      </div>

      {/* Middle - Absolute center */}
      <div className="text-center">
        <div className="inline-flex items-baseline gap-4">
          <p className="text-[180px] font-black text-transparent bg-linear-to-r from-white via-purple-100 to-white bg-clip-text drop-shadow-2xl leading-none">
            {totalHours.toFixed(1)}
          </p>
          <p className="text-4xl font-normal text-white/80">hours</p>
        </div>
      </div>

      {/* Bottom */}
      <div className="text-center pb-8">
        <p className="text-3xl font-normal text-white/80">
          Hopefully you used that time wisely... right?
        </p>
      </div>
    </div>
  );
}
