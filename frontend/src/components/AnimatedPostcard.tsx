import Postcard from "./Postcard";

interface AnimatedPostcardProps {
  contentHtml?: React.ReactNode;
  background: string;
  width: number;
  height: number;
  zIndex: number;
  isAnimating: boolean;
}

export default function AnimatedPostcard({
  contentHtml,
  background,
  width,
  height,
  zIndex,
  isAnimating,
}: AnimatedPostcardProps) {
  return (
    <div
      className={`absolute transition-all duration-600 ${
        isAnimating ? "animate-swoop-out" : ""
      }`}
      style={{
        left: "50%",
        top: "50%",
        transform: "translate(-50%, -50%)",
        width: `${width}px`,
        height: `${height}px`,
        zIndex: zIndex,
      }}
    >
      <Postcard
        contentHtml={contentHtml}
        background={background}
        rotation={0}
        zIndex={zIndex}
        offset={{ x: 0, y: 0 }}
        width={width}
        height={height}
      />
    </div>
  );
}
