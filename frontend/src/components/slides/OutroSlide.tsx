"use client";

export default function OutroSlide() {
  return (
    <div className="w-full h-full flex flex-col items-center justify-center p-12 bg-linear-to-br from-purple-950 via-purple-900 to-indigo-950">
      <div className="max-w-4xl mx-auto text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-7xl font-black text-transparent bg-linear-to-r from-purple-200 via-pink-200 to-purple-300 bg-clip-text animate-in fade-in slide-in-from-bottom-4 duration-700">
            That's the Rewind!
          </h1>
          <p className="text-xl text-white/80 animate-in fade-in slide-in-from-bottom-6 duration-700">
            Thank you for using GPT Rewind to explore your ChatGPT history. We
            hope you learned something new about your conversation patterns and
            topics.
          </p>
        </div>
      </div>
    </div>
  );
}
