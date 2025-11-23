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

const MONTH_NAMES = [
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

export default function MonthlyActivitySlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Extract labels and values from data
  const labels = Object.keys(data).map((dateStr) => {
    const [, month] = dateStr.split("-");
    return MONTH_NAMES[parseInt(month) - 1];
  });

  const values = Object.values(data);

  const chartData = {
    labels,
    datasets: [
      {
        label: "Hours per Month",
        data: values,
        backgroundColor: "#a78bfa",
        borderColor: "#8b5cf6",
        borderWidth: 2,
        borderRadius: 6,
        barThickness: 40,
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
        padding: 12,
        titleFont: { size: 14, weight: "bold" as const },
        bodyFont: { size: 13 },
        callbacks: {
          label: (context: any) => `${context.parsed.y.toFixed(1)} hours`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: "#1f2937",
          font: { size: 12, weight: 500 },
          callback: (value: any) => value + "h",
        },
        grid: { color: "rgba(0, 0, 0, 0.05)", lineWidth: 1 },
        border: { display: false },
      },
      x: {
        ticks: {
          color: "#1f2937",
          font: { size: 13, weight: 600 },
        },
        grid: { display: false },
        border: { display: false },
      },
    },
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-12 bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950">
      <div className="w-full max-w-5xl space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-5xl font-bold text-white pt-4">
            Monthly Activity
          </h2>
        </div>

        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-8 shadow-sm border border-purple-700/30">
          <div className="h-[400px]">
            <Bar data={chartData} options={options} />
          </div>
        </div>
      </div>
    </div>
  );
}
