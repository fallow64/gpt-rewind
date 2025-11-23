"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const TIME_LABELS = [
  "Night\n(12-6am)",
  "Morning\n(6am-12pm)",
  "Afternoon\n(12-6pm)",
  "Evening\n(6pm-12am)",
];

const TIME_EMOJIS = ["🌙", "☀️", "🌤️", "🌆"];

export default function TimeOfDaySlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  // Expecting: { timeOfDayHours: [night, morning, afternoon, evening] }
  const timeOfDayHours = data.timeOfDayHours || [0, 0, 0, 0];

  const chartData = {
    labels: TIME_LABELS,
    datasets: [
      {
        label: "Hours",
        data: timeOfDayHours,
        backgroundColor: [
          "#7c3aed", // Night - purple
          "#a78bfa", // Morning - lighter purple
          "#c4b5fd", // Afternoon - light purple
          "#8b5cf6", // Evening - medium purple
        ],
        borderColor: ["#6d28d9", "#8b5cf6", "#a78bfa", "#7c3aed"],
        borderWidth: 2,
        borderRadius: 8,
        barThickness: 80,
      },
    ],
  };

  const options = {
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
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        padding: 12,
        titleFont: {
          size: 14,
          weight: "bold" as const,
        },
        bodyFont: {
          size: 13,
        },
        callbacks: {
          label: function (context: any) {
            return `${context.parsed.y.toFixed(1)} hours`;
          },
        },
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
            size: 14,
            weight: 600 as const,
          },
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: "rgba(139, 92, 246, 0.1)",
        },
        ticks: {
          color: "#e9d5ff",
          font: {
            size: 12,
          },
          callback: function (value: any) {
            return value + "h";
          },
        },
      },
    },
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950 p-12">
      <div className="w-full max-w-4xl space-y-8">
        {/* Header */}
        <div className="text-center space-y-3">
          <h2 className="text-5xl font-bold text-white">When You Chat</h2>
          <p className="text-xl text-purple-200">
            Your GPT activity by time of day
          </p>
        </div>

        {/* Chart */}
        <div className="bg-purple-900/30 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-purple-700/30">
          <div className="h-[400px]">
            <Bar data={chartData} options={options} />
          </div>
        </div>

        {/* Time period emojis */}
        <div className="flex justify-around text-6xl opacity-80">
          {TIME_EMOJIS.map((emoji, idx) => (
            <div key={idx} className="flex flex-col items-center gap-2">
              <span>{emoji}</span>
              <span className="text-xs text-purple-300 font-medium">
                {timeOfDayHours[idx].toFixed(0)}h
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
