"use client";

import { ReactNode, useState } from "react";
import AnimatedPostcardStack from "@/src/components/postcard/AnimatedPostcardStack";
import NextButton from "@/src/components/layout/NextButton";
import BackButton from "@/src/components/layout/BackButton";
import { POSTCARD_CONFIG, DEFAULT_BACKGROUND_CARDS } from "../types";
import TopicsPerHourSlide from "@/src/components/slides/TopicsPerHourSlide";
import TopTopicsThisYearSlide from "@/src/components/slides/TopTopicsThisYearSlide";
import PostcardStack from "@/src/components/postcard/PostcardStack";

const postcardData: ReactNode[] = [
  <TopTopicsThisYearSlide />,
  <TopicsPerHourSlide />,

  <div className="w-full h-full space-y-6 bg-red-300">
    <h2 className="text-4xl font-bold text-gray-900">Your topics over time</h2>
    <div className="text-gray-800">
      <p className="text-xl mb-4">Your interests have evolved significantly!</p>
      <ul className="list-disc list-inside text-left space-y-2 text-lg">
        <li>2022: Travel and Adventure</li>
        <li>2023: Technology and AI</li>
        <li>2024: Personal Development</li>
        <li>(insert chart here)</li>
      </ul>
    </div>
  </div>,
];

export default function Home() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  const handleNext = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev + 1) % postcardData.length);
      setIsAnimating(false);
    }, POSTCARD_CONFIG.animationDuration);
  };

  const handleBack = () => {
    if (isAnimating) return;
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentIndex(
        (prev) => (prev - 1 + postcardData.length) % postcardData.length
      );
      setIsAnimating(false);
    }, POSTCARD_CONFIG.animationDuration);
  };

  return (
    <div
      className="relative overflow-hidden bg-linear-to-br from-gray-950 via-gray-900 to-black"
      style={{ minHeight: "calc(100vh - 64px)" }}
    >
      {/* Abstract table texture - dark effect */}
      <div className="absolute inset-0 opacity-20">
        <div className="h-full w-full bg-linear-to-b from-gray-800/30 via-transparent to-gray-950/30"></div>
        <div className="absolute inset-0 bg-[repeating-linear-gradient(90deg,transparent,transparent_2px,rgba(0,0,0,0.1)_2px,rgba(0,0,0,0.1)_4px)]"></div>
      </div>

      <main
        className="relative flex items-center justify-center p-8"
        style={{ minHeight: "calc(100vh - 64px)" }}
      >
        {/* Stack of postcards - all positioned absolutely and centered */}
        <PostcardStack
          postcards={DEFAULT_BACKGROUND_CARDS}
          width={1280}
          height={720}
          background="#304158ff"
        />

        {/* Animated postcard stack with current and next */}
        <AnimatedPostcardStack
          postcards={postcardData}
          currentIndex={currentIndex}
          isAnimating={isAnimating}
          width={1280}
          height={720}
          baseZIndex={DEFAULT_BACKGROUND_CARDS.length}
        />

        {/* Navigation buttons */}
        <BackButton
          onClick={handleBack}
          disabled={isAnimating || currentIndex === 0}
        />
        <NextButton onClick={handleNext} disabled={isAnimating} />
      </main>
    </div>
  );
}
