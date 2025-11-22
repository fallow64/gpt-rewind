import { ReactNode } from "react";
import AnimatedPostcard from "./AnimatedPostcard";

interface AnimatedPostcardStackProps {
  postcards: ReactNode[];
  currentIndex: number;
  isAnimating: boolean;
  width: number;
  height: number;
  baseZIndex: number;
}

export default function AnimatedPostcardStack({
  postcards,
  currentIndex,
  isAnimating,
  width,
  height,
  baseZIndex,
}: AnimatedPostcardStackProps) {
  const nextIndex = (currentIndex + 1) % postcards.length;

  return (
    <>
      {/* Next postcard (second in stack) */}
      <AnimatedPostcard
        key={`next-${nextIndex}`}
        content={postcards[nextIndex]}
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
