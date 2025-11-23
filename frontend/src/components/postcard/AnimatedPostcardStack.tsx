import { ReactNode } from "react";
import AnimatedPostcard from "./AnimatedPostcard";

interface AnimatedPostcardStackProps {
  postcards: ReactNode[];
  currentIndex: number;
  isAnimating: boolean;
  direction: "forward" | "backward";
  width: number;
  height: number;
  baseZIndex: number;
}

export default function AnimatedPostcardStack({
  postcards,
  currentIndex,
  isAnimating,
  direction,
  width,
  height,
  baseZIndex,
}: AnimatedPostcardStackProps) {
  // Show next card when going forward, previous card when going backward
  const adjacentIndex =
    direction === "forward"
      ? (currentIndex + 1) % postcards.length
      : (currentIndex - 1 + postcards.length) % postcards.length;

  return (
    <>
      {/* Adjacent postcard (second in stack) - next or previous based on direction */}
      <AnimatedPostcard
        key={`adjacent-${adjacentIndex}`}
        content={postcards[adjacentIndex]}
        width={width}
        height={height}
        zIndex={baseZIndex}
        isAnimating={false}
      />

      {/* Current postcard (top of stack) */}
      <AnimatedPostcard
        key={`current-${currentIndex}`}
        content={postcards[currentIndex]}
        width={width}
        height={height}
        zIndex={baseZIndex + 1}
        isAnimating={isAnimating}
      />
    </>
  );
}
