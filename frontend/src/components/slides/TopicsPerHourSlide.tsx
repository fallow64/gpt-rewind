"use client";

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

interface TopicData {
  hour: string;
  topic: string;
  count: number;
}

const sampleData: TopicData[] = [
  { hour: "12 AM", topic: "Sleep & Dreams", count: 5 },
  { hour: "3 AM", topic: "Late Night Thoughts", count: 3 },
  { hour: "6 AM", topic: "Morning Routines", count: 8 },
  { hour: "9 AM", topic: "Work & Productivity", count: 15 },
  { hour: "12 PM", topic: "Lunch Ideas", count: 12 },
  { hour: "3 PM", topic: "Learning & Skills", count: 18 },
  { hour: "6 PM", topic: "Dinner & Cooking", count: 10 },
  { hour: "9 PM", topic: "Entertainment", count: 14 },
];

function TopicsPerHourSlide() {
  const chartData = {
    labels: sampleData.map((d) => d.hour),
    datasets: [
      {
        label: "Messages",
        data: sampleData.map((d) => d.count),
        backgroundColor: "rgba(102, 126, 234, 0.8)",
        borderColor: "rgba(102, 126, 234, 1)",
        borderWidth: 2,
        borderRadius: 8,
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
        enabled: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: "rgba(255, 255, 255, 0.1)",
        },
        ticks: {
          color: "rgba(255, 255, 255, 0.7)",
          font: {
            size: 14,
          },
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: "rgba(255, 255, 255, 0.7)",
          font: {
            size: 14,
          },
        },
      },
    },
  };

  return (
    <div className="w-full h-full flex flex-col items-center justify-center space-y-8 p-8 bg-linear-to-br from-purple-800 via-indigo-900 to-blue-900">
      <h2 className="text-4xl font-bold text-white">Your Topics By Time</h2>
      <p className="text-xl text-white/80">
        What you talked about throughout the day
      </p>

      {/* Chart Container */}
      <div className="w-full h-96">
        <Bar data={chartData} options={options} />
      </div>

      {/* Topic Labels Below Chart */}
      <div className="grid grid-cols-4 gap-4 w-full max-w-4xl">
        {sampleData.map((item, index) => (
          <div
            key={index}
            className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center"
          >
            <div className="text-sm text-white/60 mb-1">{item.hour}</div>
            <div className="text-base font-semibold text-white">
              {item.topic}
            </div>
            <div className="text-sm text-white/70 mt-1">
              {item.count} messages
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TopicsPerHourSlide;
