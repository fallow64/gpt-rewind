"use client";

interface TopicData {
  rank: number;
  topic: string;
  count: number;
  color: string;
}

const sampleData: TopicData[] = [
  {
    rank: 1,
    topic: "AI & Technology",
    count: 245,
    color: "rgba(255, 99, 132, 1)",
  },
  {
    rank: 2,
    topic: "Programming",
    count: 198,
    color: "rgba(54, 162, 235, 1)",
  },
  {
    rank: 3,
    topic: "Career Advice",
    count: 156,
    color: "rgba(255, 206, 86, 1)",
  },
];

function TopTopicsThisYearSlide() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-12 bg-linear-to-br from-pink-600 via-purple-700 to-indigo-800">
      <h2 className="text-6xl font-bold text-white mb-4">
        Your Top Topics This Year
      </h2>
      <p className="text-2xl text-white/90 mb-16">
        Your most discussed subjects in 2024
      </p>

      {/* Large Topic Cards - Podium Style */}
      <div className="flex items-end justify-center gap-8 w-full max-w-4xl">
        {/* Rank #2 - Silver */}
        <div
          className="flex flex-col items-center justify-end"
          style={{ height: "400px" }}
        >
          <div className="text-8xl mb-4">🥈</div>
          <div
            className="w-64 rounded-t-3xl p-8 text-center shadow-2xl border-4 flex flex-col justify-between"
            style={{
              backgroundColor: sampleData[1].color,
              borderColor: "rgba(192, 192, 192, 0.8)",
              height: "280px",
            }}
          >
            <div>
              <div className="text-7xl font-black text-white mb-3">#2</div>
              <div className="text-2xl font-bold text-white mb-4">
                {sampleData[1].topic}
              </div>
            </div>
            <div className="text-4xl font-bold text-white">
              {sampleData[1].count}
            </div>
          </div>
        </div>

        {/* Rank #1 - Gold */}
        <div
          className="flex flex-col items-center justify-end"
          style={{ height: "400px" }}
        >
          <div className="text-9xl mb-4">🏆</div>
          <div
            className="w-72 rounded-t-3xl p-8 text-center shadow-2xl border-4 flex flex-col justify-between"
            style={{
              backgroundColor: sampleData[0].color,
              borderColor: "rgba(255, 215, 0, 0.8)",
              height: "320px",
            }}
          >
            <div>
              <div className="text-8xl font-black text-white mb-3">#1</div>
              <div className="text-2xl font-bold text-white mb-4">
                {sampleData[0].topic}
              </div>
            </div>
            <div className="text-5xl font-bold text-white">
              {sampleData[0].count}
            </div>
          </div>
        </div>

        {/* Rank #3 - Bronze */}
        <div
          className="flex flex-col items-center justify-end"
          style={{ height: "400px" }}
        >
          <div className="text-8xl mb-4">🥉</div>
          <div
            className="w-64 rounded-t-3xl p-8 text-center shadow-2xl border-4 flex flex-col justify-between"
            style={{
              backgroundColor: sampleData[2].color,
              borderColor: "rgba(205, 127, 50, 0.8)",
              height: "240px",
            }}
          >
            <div>
              <div className="text-7xl font-black text-white mb-3">#3</div>
              <div className="text-2xl font-bold text-white mb-4">
                {sampleData[2].topic}
              </div>
            </div>
            <div className="text-4xl font-bold text-white">
              {sampleData[2].count}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default TopTopicsThisYearSlide;
