"use client";

import { useMemo } from "react";
import { useSlide } from "@/src/contexts/SlideDataContext";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

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

  const chartData = useMemo(
    () => ({
      labels: MONTH_LABELS,
      datasets: [
        {
          label: "Top Topic",
          data: MONTH_LABELS.map((_, idx) => idx), // Just for positioning
          backgroundColor: "transparent",
          borderColor: "transparent",
          pointRadius: 0,
        },
      ],
    }),
    []
  );

  const options = useMemo(
    () => ({
      responsive: true,
      maintainAspectRatio: false,
      animation: false as const,
      plugins: {
        legend: {
          display: false,
        },
        title: {
          display: false,
        },
        tooltip: {
          enabled: false,
        },
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
          ticks: {
            color: "#e9d5ff",
            font: {
              size: 13,
              weight: 600,
            },
          },
          border: {
            display: false,
          },
        },
        y: {
          display: false,
        },
      },
    }),
    []
  );

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
          {/* Custom topic display */}
          <div className="space-y-4">
            {MONTH_LABELS.map((month, idx) => (
              <div
                key={month}
                className="flex items-center gap-6 py-3 px-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
              >
                <div className="text-purple-300 font-semibold text-lg min-w-[60px]">
                  {month}
                </div>
                <div className="flex-1 h-px bg-purple-500/30"></div>
                <div className="text-white text-lg font-medium">
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
