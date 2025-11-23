"use client";

import { useMemo } from "react";
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

export default function MonthlyActivitySlide() {
  const { data, error } = useSlide();

  if (error) {
    throw error;
  }

  const chartData = useMemo(
    () => ({
      datasets: [
        {
          label: "Hours per Month",
          data: data,
          backgroundColor: "#a78bfa",
          borderColor: "#8b5cf6",
          borderWidth: 2,
          borderRadius: 6,
          barThickness: 40,
        },
      ],
    }),
    [data]
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
            callback: function (value: any, index: number) {
              const label = chartData.datasets[0].data[index]?.x;
              if (typeof label === "string") {
                const [, month] = label.split("-");
                const monthNames = [
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
                return monthNames[parseInt(month) - 1];
              }
              return label;
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
    }),
    []
  );

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
