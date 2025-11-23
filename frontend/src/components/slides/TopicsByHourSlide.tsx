"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";

const HOURS = [
  "12am",
  "1am",
  "2am",
  "3am",
  "4am",
  "5am",
  "6am",
  "7am",
  "8am",
  "9am",
  "10am",
  "11am",
  "12pm",
  "1pm",
  "2pm",
  "3pm",
  "4pm",
  "5pm",
  "6pm",
  "7pm",
  "8pm",
  "9pm",
  "10pm",
  "11pm",
];

const TIME_PERIODS = [
  {
    start: 0,
    end: 6,
    label: "Late Night",
    color: "from-indigo-900/40 to-purple-900/40",
    borderColor: "border-indigo-500/30",
  },
  {
    start: 6,
    end: 12,
    label: "Morning",
    color: "from-amber-900/40 to-yellow-900/40",
    borderColor: "border-amber-500/30",
  },
  {
    start: 12,
    end: 18,
    label: "Afternoon",
    color: "from-orange-900/40 to-red-900/40",
    borderColor: "border-orange-500/30",
  },
  {
    start: 18,
    end: 24,
    label: "Evening",
    color: "from-purple-900/40 to-indigo-900/40",
    borderColor: "border-purple-500/30",
  },
];

export default function TopicsByHourSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  // Expecting: { hourlyTopics: ["Topic", "Topic", ...] } - 24 topics, one per hour
  const hourlyTopics = data.hourlyTopics || Array(24).fill("General");

  const getTimePeriod = (hour: number) => {
    return (
      TIME_PERIODS.find(
        (period) => hour >= period.start && hour < period.end
      ) || TIME_PERIODS[0]
    );
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-12 bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950">
      <div className="w-full max-w-6xl space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-5xl font-bold text-white">
            Topics Throughout Your Day
          </h2>
          <p className="text-xl text-purple-200">
            What you talk about at different hours
          </p>
        </div>

        <div className="bg-purple-900/30 backdrop-blur-sm rounded-2xl p-6 shadow-sm border border-purple-700/30">
          {/* Hour-by-hour grid */}
          <div className="grid grid-cols-2 gap-3 max-h-[500px] overflow-y-auto">
            {HOURS.map((hour, idx) => {
              const period = getTimePeriod(idx);
              return (
                <div
                  key={hour}
                  className={`flex items-center gap-4 py-2 px-4 bg-linear-to-r ${period.color} rounded-lg border ${period.borderColor} hover:scale-[1.02] transition-transform`}
                >
                  <div className="text-purple-200 font-semibold text-sm min-w-[50px]">
                    {hour}
                  </div>
                  <div className="flex-1 h-px bg-purple-500/20"></div>
                  <div className="text-white text-sm font-medium text-right">
                    {hourlyTopics[idx]}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="text-center">
          <p className="text-sm text-purple-200">
            Your conversation topics follow your daily rhythm
          </p>
        </div>
      </div>
    </div>
  );
}
