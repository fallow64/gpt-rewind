"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";

const MONTH_LABELS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];

export default function TopicsByMonthSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  // Expecting: { monthlyTopics: ["Topic A", "Topic B", ...] } - 12 topics, one per month
  const monthlyTopics = data.monthlyTopics || Array(12).fill("General");

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
            {MONTH_LABELS.map((month, idx) => (
              <div
                key={month}
                className="flex flex-col items-center gap-3 py-4 px-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
              >
                <div className="text-purple-300 font-semibold text-sm">
                  {month}
                </div>
                <div className="text-white text-base font-medium text-center">
                  {monthlyTopics[idx]}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="text-center">
          <p className="text-lg text-purple-200">
            Your conversations shifted focus{" "}
            <span className="font-semibold text-white">
              {new Set(monthlyTopics).size}
            </span>{" "}
            {new Set(monthlyTopics).size === 1 ? "time" : "times"} this year
          </p>
        </div>
      </div>
    </div>
  );
}
