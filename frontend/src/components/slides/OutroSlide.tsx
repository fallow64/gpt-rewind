"use client";

export default function OutroSlide() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-12 bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950">
      <div className="max-w-4xl mx-auto text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-7xl font-black text-transparent bg-linear-to-r from-purple-200 via-pink-200 to-purple-300 bg-clip-text animate-in fade-in slide-in-from-bottom-4 duration-700">
            That's a Wrap!
          </h1>
          <p className="text-2xl text-purple-200 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-150">
            Thank you for exploring your year with GPT
          </p>
        </div>

        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-300">
          <p className="text-xl text-purple-100 leading-relaxed">
            Every conversation, every question, every insight—
            <br />
            they all tell the story of your journey this year.
          </p>
          <p className="text-lg text-purple-200">
            Here's to more discoveries in the year ahead. 🎉
          </p>
        </div>

        <div className="pt-8 animate-in fade-in duration-700 delay-500">
          <div className="inline-block px-8 py-3 bg-purple-500/20 backdrop-blur-sm border border-purple-400/30 rounded-full">
            <p className="text-purple-200 text-sm font-medium">
              Made with ❤️ using GPT
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
