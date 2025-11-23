"use client";

import { ReactNode, useState, useEffect, Suspense } from "react";
import { useSession } from "next-auth/react";
import { redirect } from "next/navigation";
import AnimatedPostcardStack from "@/src/components/postcard/AnimatedPostcardStack";
import BackButton from "@/src/components/layout/BackButton";
import { POSTCARD_CONFIG, DEFAULT_BACKGROUND_CARDS } from "../../types";
import IntroSlide from "@/src/components/slides/IntroSlide";
import YearlyHoursSlide from "@/src/components/slides/YearlyHoursSlide";
import MonthlyHoursSlide from "@/src/components/slides/MonthlyHoursSlide";
import TimeOfDaySlide from "@/src/components/slides/TimeOfDaySlide";
import LongestConversationSlide from "@/src/components/slides/LongestConversationSlide";
import EasiestQuestionSlide from "@/src/components/slides/EasiestQuestionSlide";
import HardestQuestionSlide from "@/src/components/slides/HardestQuestionSlide";
import EstimatedProfessionSlide from "@/src/components/slides/EstimatedProfessionSlide";
import TopTopicsSlide from "@/src/components/slides/TopTopicsSlide";
import TopicsByMonthSlide from "@/src/components/slides/TopicsByMonthSlide";
import PostcardStack from "@/src/components/postcard/PostcardStack";
import NextButton from "@/src/components/layout/NextButton";
import { SlideDataProvider } from "@/src/contexts/SlideDataContext";

const LoadingSlide = () => (
  <div className="w-full h-full flex items-center justify-center bg-white">
    <div className="text-gray-900 text-2xl">Loading...</div>
  </div>
);

export default function InsightsPage() {
  const { data: session, status } = useSession();
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

  const postcards: ReactNode[] = [
    <IntroSlide key="intro" onContinue={handleNext} />,
    <Suspense key="total-hours-suspense" fallback={<LoadingSlide />}>
      <SlideDataProvider slide={1}>
        <YearlyHoursSlide />
      </SlideDataProvider>
    </Suspense>,
    <Suspense key="monthly-hours-suspense" fallback={<LoadingSlide />}>
      <SlideDataProvider slide={2}>
        <MonthlyHoursSlide />
      </SlideDataProvider>
    </Suspense>,
    <Suspense key="time-of-day-suspense" fallback={<LoadingSlide />}>
      <SlideDataProvider slide={3}>
        <TimeOfDaySlide />
      </SlideDataProvider>
    </Suspense>,
    <Suspense key="longest-conversation-suspense" fallback={<LoadingSlide />}>
      <SlideDataProvider slide={4}>
        <LongestConversationSlide />
      </SlideDataProvider>
    </Suspense>,
    <Suspense key="easiest-question-suspense" fallback={<LoadingSlide />}>
      <SlideDataProvider slide={5}>
        <EasiestQuestionSlide />
      </SlideDataProvider>
    </Suspense>,
    <Suspense key="hardest-question-suspense" fallback={<LoadingSlide />}>
      <SlideDataProvider slide={6}>
        <HardestQuestionSlide />
      </SlideDataProvider>
    </Suspense>,
    <Suspense key="estimated-profession-suspense" fallback={<LoadingSlide />}>
      <SlideDataProvider slide={7}>
        <EstimatedProfessionSlide />
      </SlideDataProvider>
    </Suspense>,
    <Suspense key="top-topics-suspense" fallback={<LoadingSlide />}>
      <SlideDataProvider slide={8}>
        <TopTopicsSlide />
      </SlideDataProvider>
    </Suspense>,
    <Suspense key="topics-by-month-suspense" fallback={<LoadingSlide />}>
      <SlideDataProvider slide={9}>
        <TopicsByMonthSlide />
      </SlideDataProvider>
    </Suspense>,
  ];

  // Redirect if not authenticated
  useEffect(() => {
    if (status === "unauthenticated") {
      redirect("/");
    }
  }, [status]);

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

  // Show loading state while checking auth
  if (status === "loading") {
    return (
      <div className="flex items-center justify-center min-h-screen bg-linear-to-br from-gray-950 via-gray-900 to-black">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!session) {
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
          width={1280}
          height={720}
          background="#304158ff"
        />

        {/* Animated postcard stack with current and next */}
        <AnimatedPostcardStack
          postcards={postcards}
          currentIndex={currentIndex}
          isAnimating={isAnimating}
          direction={direction}
          width={1280}
          height={720}
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
