import AnimatedPostcard from "./AnimatedPostcard";
import { PostcardData } from "@/src/types";

interface AnimatedPostcardStackProps {
  postcards: PostcardData[];
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
        contentHtml={postcards[nextIndex].contentHtml}
        background={postcards[nextIndex].background}
        width={width}
        height={height}
        zIndex={baseZIndex}
        isAnimating={false}
      />

      {/* Current postcard (top of stack) */}
      <AnimatedPostcard
        key={`current-${currentIndex}`}
        contentHtml={postcards[currentIndex].contentHtml}
        background={postcards[currentIndex].background}
        width={width}
        height={height}
        zIndex={baseZIndex + 1}
        isAnimating={isAnimating}
      />
    </>
  );
}
