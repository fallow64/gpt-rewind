"use client";

import { useSlide } from "@/src/contexts/SlideDataContext";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip);

const HOUR_LABELS = [
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

const getHourColor = (hour: number) => {
  if (hour >= 0 && hour < 6) return "#6d28d9"; // Night - deep purple
  if (hour >= 6 && hour < 12) return "#a78bfa"; // Morning - light purple
  if (hour >= 12 && hour < 18) return "#c4b5fd"; // Afternoon - lighter purple
  return "#8b5cf6"; // Evening - medium purple
};

export default function WhenYouChatSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Convert data object like {"0": 10, "1": 20, ..., "23": 15} to array
  const hourlyActivity = Array.from(
    { length: 24 },
    (_, i) => data[String(i)] || 0
  );

  const chartData = {
    labels: HOUR_LABELS,
    datasets: [
      {
        label: "Activity",
        data: hourlyActivity,
        backgroundColor: HOUR_LABELS.map((_, idx) => getHourColor(idx)),
        borderColor: HOUR_LABELS.map((_, idx) => getHourColor(idx)),
        borderWidth: 2,
        borderRadius: 6,
        barThickness: 20,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false as const,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        padding: 10,
        titleFont: { size: 13, weight: "bold" as const },
        bodyFont: { size: 12 },
        callbacks: {
          label: (context: any) => `${context.parsed.y.toFixed(1)} messages`,
        },
      },
    },
    scales: {
      x: {
        grid: { display: false },
        ticks: {
          color: "#1f2937",
          font: { size: 10, weight: 500 as const },
          maxRotation: 0,
          minRotation: 0,
        },
      },
      y: {
        beginAtZero: true,
        grid: { color: "rgba(0, 0, 0, 0.05)" },
        ticks: {
          color: "#4b5563",
          font: { size: 11 },
        },
      },
    },
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950 p-12">
      <div className="w-full max-w-6xl space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h2 className="text-4xl font-bold text-white">When You Chat</h2>
          <p className="text-lg text-purple-200">
            Your activity throughout the day
          </p>
        </div>

        {/* Chart */}
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-xl p-6 border border-purple-700/30">
          <div className="h-[450px]">
            <Bar data={chartData} options={options} />
          </div>
        </div>

        {/* Summary */}
        {/* <div className="text-center">
          <p className="text-sm text-purple-200">
            Peak activity:{" "}
            <span className="text-white font-bold">
              {HOUR_LABELS[hourlyActivity.indexOf(Math.max(...hourlyActivity))]}
            </span>
          </p>
        </div> */}
      </div>
    </div>
  );
}
