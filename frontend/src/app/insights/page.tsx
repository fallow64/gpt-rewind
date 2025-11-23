"use client";

import BackButton from "@/src/components/layout/BackButton";
import NextButton from "@/src/components/layout/NextButton";
import AnimatedPostcardStack from "@/src/components/postcard/AnimatedPostcardStack";
import PostcardStack from "@/src/components/postcard/PostcardStack";
import EasiestQuestionSlide from "@/src/components/slides/EasiestQuestionSlide";
import HardestQuestionSlide from "@/src/components/slides/HardestQuestionSlide";
import IntroSlide from "@/src/components/slides/IntroSlide";
import MonthlyActivitySlide from "@/src/components/slides/MonthlyActivitySlide";
import OutroSlide from "@/src/components/slides/OutroSlide";
import TopicsByHourSlide from "@/src/components/slides/TopicsByHourSlide";
import TopicsByMonthSlide from "@/src/components/slides/TopicsByMonthSlide";
import WhenYouChatSlide from "@/src/components/slides/WhenYouChatSlide";
import YearlyHoursSlide from "@/src/components/slides/YearlyHoursSlide";
import YourLongestConversationSlide from "@/src/components/slides/YourLongestConversationSlide";
import YourTopTopicsSlide from "@/src/components/slides/YourTopTopicsSlide";
import { SlideDataProvider } from "@/src/contexts/SlideDataContext";
import { ReactNode, Suspense, useEffect, useState } from "react";
import { DEFAULT_BACKGROUND_CARDS, POSTCARD_CONFIG } from "../../types";

const LoadingSlide = () => (
  <div className="w-full h-full flex items-center justify-center bg-white">
    <div className="text-gray-900 text-2xl">Loading...</div>
  </div>
);

export default function InsightsPage() {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [direction, setDirection] = useState<"forward" | "backward">("forward");

  const handleNext = () => {
    if (isAnimating) return;
    setDirection("forward");
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev + 1) % postcards.length);
      setIsAnimating(false);
    }, POSTCARD_CONFIG.animationDuration);
  };

  const slides = [
    { key: "intro", component: IntroSlide, slide: -1 },
    { key: "total-hours", component: YearlyHoursSlide, slide: 0 },
    { key: "monthly-hours", component: MonthlyActivitySlide, slide: 1 },
    { key: "time-of-day", component: WhenYouChatSlide, slide: 2 },
    {
      key: "longest-conversation",
      component: YourLongestConversationSlide,
      slide: 3,
    },
    { key: "easiest-question", component: EasiestQuestionSlide, slide: 4 },
    { key: "hardest-question", component: HardestQuestionSlide, slide: 5 },
    { key: "top-topics", component: YourTopTopicsSlide, slide: 6 },
    { key: "topics-by-month", component: TopicsByMonthSlide, slide: 7 },
    { key: "topics-by-hour", component: TopicsByHourSlide, slide: 8 },
    // { key: "outro", component: OutroSlide, slide: 9 },
  ];

  const postcards: ReactNode[] = slides.map(
    ({ key, component: Component, slide }) => {
      if (slide === null) {
        return <Component key={key} />;
      }
      return (
        <Suspense key={`${key}-suspense`} fallback={<LoadingSlide />}>
          <SlideDataProvider slide={slide}>
            <Component />
          </SlideDataProvider>
        </Suspense>
      );
    }
  );

  const handleBack = () => {
    if (isAnimating) return;
    setDirection("backward");
    setIsAnimating(true);
    setTimeout(() => {
      setCurrentIndex(
        (prev) => (prev - 1 + postcards.length) % postcards.length
      );
      setIsAnimating(false);
    }, POSTCARD_CONFIG.animationDuration);
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "ArrowRight") {
        handleNext();
      } else if (event.key === "ArrowLeft") {
        handleBack();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isAnimating, currentIndex]);

  if (!isMounted) {
    return null;
  }

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
          width={POSTCARD_CONFIG.width}
          height={POSTCARD_CONFIG.height}
          background="#304158ff"
        />

        {/* Animated postcard stack with current and next */}
        <AnimatedPostcardStack
          postcards={postcards}
          currentIndex={currentIndex}
          isAnimating={isAnimating}
          direction={direction}
          width={POSTCARD_CONFIG.width}
          height={POSTCARD_CONFIG.height}
          baseZIndex={DEFAULT_BACKGROUND_CARDS.length}
        />

        {/* Navigation buttons */}
        {currentIndex !== 0 && (
          <BackButton onClick={handleBack} disabled={isAnimating} />
        )}
        {currentIndex < postcards.length - 1 && (
          <NextButton onClick={handleNext} disabled={isAnimating} />
        )}
      </main>
    </div>
  );
}
