import Image from "next/image";

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-gradient-to-br from-amber-100 via-orange-50 to-amber-50">
      {/* Abstract table texture - wood grain effect */}
      <div className="absolute inset-0 opacity-30">
        <div className="h-full w-full bg-gradient-to-b from-amber-200/50 via-transparent to-amber-300/30"></div>
        <div className="absolute inset-0 bg-[repeating-linear-gradient(90deg,transparent,transparent_2px,rgba(180,83,9,0.03)_2px,rgba(180,83,9,0.03)_4px)]"></div>
      </div>

      <main className="relative flex min-h-screen items-center justify-center p-8">
        {/* Stack of notepapers */}
        <div className="relative">
          {/* Bottom notepaper - rotated slightly */}
          <div className="absolute -bottom-4 -right-4 h-96 w-80 rounded-lg bg-gradient-to-br from-yellow-100 to-yellow-200 shadow-xl rotate-3 opacity-70"></div>

          {/* Middle notepaper - rotated opposite */}
          <div className="absolute -bottom-2 -left-3 h-96 w-80 rounded-lg bg-gradient-to-br from-blue-100 to-blue-200 shadow-xl -rotate-2 opacity-80"></div>

          {/* Top notepaper - main card */}
          <div className="relative h-96 w-80 rounded-lg bg-gradient-to-br from-pink-50 to-rose-100 shadow-2xl transform transition-transform hover:scale-105">
            {/* Content area */}
            <div className="relative p-8 h-full flex flex-col justify-center items-center text-center">
              <div className="space-y-4">
                <h2 className="text-3xl font-bold text-gray-800">
                  Postcard Title
                </h2>
                <p className="text-gray-600">Your content goes here</p>
                <div className="pt-4">
                  <div className="h-32 w-full rounded-md bg-white/50 backdrop-blur-sm flex items-center justify-center text-gray-400">
                    Content Block
                  </div>
                </div>
              </div>
            </div>

            {/* Corner fold effect */}
            <div className="absolute top-0 right-0 w-12 h-12 overflow-hidden">
              <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-gray-200 to-gray-300 rotate-45 translate-x-8 -translate-y-8 shadow-inner"></div>
            </div>
          </div>

          {/* Additional scattered notepapers for depth */}
          <div className="absolute -top-8 -right-12 h-32 w-40 rounded-md bg-gradient-to-br from-green-100 to-emerald-200 shadow-lg rotate-12 opacity-60"></div>
          <div className="absolute -bottom-6 right-8 h-24 w-32 rounded-md bg-gradient-to-br from-purple-100 to-violet-200 shadow-lg -rotate-6 opacity-50"></div>
        </div>
      </main>
    </div>
  );
}
