"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";

const TIME_PERIODS = [
  {
    name: "Night",
    start: 0,
    end: 6,
    color: "from-indigo-900/40 to-indigo-800/40",
    emoji: "🌙",
  },
  {
    name: "Morning",
    start: 6,
    end: 12,
    color: "from-orange-900/40 to-yellow-800/40",
    emoji: "🌅",
  },
  {
    name: "Afternoon",
    start: 12,
    end: 18,
    color: "from-blue-900/40 to-blue-800/40",
    emoji: "☀️",
  },
  {
    name: "Evening",
    start: 18,
    end: 24,
    color: "from-purple-900/40 to-purple-800/40",
    emoji: "🌆",
  },
];

const formatHour = (hour: number): string => {
  if (hour === 0) return "12am";
  if (hour < 12) return `${hour}am`;
  if (hour === 12) return "12pm";
  return `${hour - 12}pm`;
};

export default function TopicsByHourSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data format: Record<number, string> where key is 0-23 (hour) and value is topic
  const hourlyData: Record<number, string> = data;

  // Group hours by time period
  const periodGroups = TIME_PERIODS.map((period) => {
    const hours = Array.from(
      { length: period.end - period.start },
      (_, i) => period.start + i
    ).filter((hour) => hourlyData[hour]); // Only include hours with data

    return {
      ...period,
      hours: hours.map((hour) => ({
        hour,
        label: formatHour(hour),
        topic: hourlyData[hour] || "No data",
      })),
    };
  }).filter((period) => period.hours.length > 0); // Only show periods with data

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

        <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
          {periodGroups.map((period) => (
            <div
              key={period.name}
              className="bg-purple-900/30 backdrop-blur-sm rounded-2xl p-4 shadow-sm border border-purple-700/30"
            >
              {/* Period Header */}
              <div className="flex items-center gap-2 mb-3">
                <span className="text-2xl">{period.emoji}</span>
                <h3 className="text-xl font-bold text-white">{period.name}</h3>
                <span className="text-purple-300 text-sm">
                  ({period.hours.length}{" "}
                  {period.hours.length === 1 ? "hour" : "hours"})
                </span>
              </div>

              {/* Hours Grid */}
              <div className="grid grid-cols-2 gap-2 gap-x-4">
                {/* Left Column - First half */}
                <div className="space-y-2">
                  {period.hours
                    .slice(0, Math.ceil(period.hours.length / 2))
                    .map(({ hour, label, topic }) => (
                      <div
                        key={hour}
                        className={`flex items-center gap-3 py-2 px-3 bg-linear-to-r ${period.color} rounded-lg hover:scale-[1.02] transition-transform`}
                      >
                        <div className="text-purple-200 font-semibold text-xs min-w-[45px]">
                          {label}
                        </div>
                        <div className="flex-1 h-px bg-purple-500/20"></div>
                        <div className="text-white text-sm font-medium text-right flex-1">
                          {topic}
                        </div>
                      </div>
                    ))}
                </div>
                {/* Right Column - Second half */}
                <div className="space-y-2">
                  {period.hours
                    .slice(Math.ceil(period.hours.length / 2))
                    .map(({ hour, label, topic }) => (
                      <div
                        key={hour}
                        className={`flex items-center gap-3 py-2 px-3 bg-linear-to-r ${period.color} rounded-lg hover:scale-[1.02] transition-transform`}
                      >
                        <div className="text-purple-200 font-semibold text-xs min-w-[45px]">
                          {label}
                        </div>
                        <div className="flex-1 h-px bg-purple-500/20"></div>
                        <div className="text-white text-sm font-medium text-right flex-1">
                          {topic}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
