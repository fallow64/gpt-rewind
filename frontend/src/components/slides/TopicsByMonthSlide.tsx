"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";
import { MONTH_NAMES } from "@/src/types";

export default function TopicsByMonthSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  const rawData = data as Record<string, string>;
  const arrayData: { month: number; topic: string }[] = Object.entries(rawData)
    .sort()
    .splice(0, 12)
    .map(([monthStr, topic]) => ({
      month: parseInt(monthStr.split("-")[1], 10),
      topic,
    }));

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-12 bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950">
      <div className="w-full max-w-6xl space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-5xl font-bold text-white">
            Your Topics Over Time
          </h2>
          <p className="text-xl text-purple-200">
            How your interests evolved throughout the year
          </p>
        </div>

        <div className="bg-purple-900/30 backdrop-blur-sm rounded-2xl p-8 shadow-sm border border-purple-700/30">
          {/* 6x2 Grid layout */}
          <div className="grid grid-cols-6 gap-4">
            {arrayData.map((arrayElement, i) => (
              <div key={i}>
                <div className="text-purple-300 text-sm mb-1">
                  {MONTH_NAMES[arrayElement.month - 1]}
                </div>
                <div className="bg-white/10 backdrop-blur-sm border-2 border-white/20 rounded-2xl px-4 py-6 h-20 flex items-center justify-center">
                  <p className="text-md font-medium text-white text-center leading-tight">
                    {arrayElement.topic}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
