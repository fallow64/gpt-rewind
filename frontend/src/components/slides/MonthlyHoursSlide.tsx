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

export default function MonthlyHoursSlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  // Data is guaranteed to exist when component renders due to Suspense
  const monthlyHours = data.monthlyHours || Array(12).fill(0);

  const chartData = {
    labels: MONTH_LABELS,
    datasets: [
      {
        label: "Hours per Month",
        data: monthlyHours,
        backgroundColor: "#3b82f6",
        borderColor: "#2563eb",
        borderWidth: 2,
        borderRadius: 6,
        barThickness: 40,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
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
      y: {
        beginAtZero: true,
        ticks: {
          color: "#1f2937",
          font: {
            size: 12,
            weight: 500,
          },
          callback: function (value: any) {
            return value + "h";
          },
        },
        grid: {
          color: "rgba(0, 0, 0, 0.05)",
          lineWidth: 1,
        },
        border: {
          display: false,
        },
      },
      x: {
        ticks: {
          color: "#1f2937",
          font: {
            size: 13,
            weight: 600,
          },
        },
        grid: {
          display: false,
        },
        border: {
          display: false,
        },
      },
    },
  };

  const totalHours = monthlyHours.reduce(
    (sum: number, hours: number) => sum + hours,
    0
  );

  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-12">
      <div className="w-full max-w-5xl space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-5xl font-bold text-gray-900">Monthly Activity</h2>
          <p className="text-xl text-gray-600">
            Your GPT usage throughout the year
          </p>
        </div>

        <div className="bg-gray-50 rounded-2xl p-8 shadow-sm border border-gray-200">
          <div className="h-[400px]">
            <Bar data={chartData} options={options} />
          </div>
        </div>

        <div className="text-center">
          <p className="text-lg text-gray-700">
            <span className="font-semibold text-gray-900">
              {totalHours.toFixed(1)} hours
            </span>{" "}
            total this year
          </p>
        </div>
      </div>
    </div>
  );
}
