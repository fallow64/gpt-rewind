import Image from "next/image";
import { PostcardProps } from "@/src/types";

const PAPER_LINE_OPACITY = 0.05;
const PAPER_LINE_COLOR = "255, 255, 255";

export default function Postcard({
  contentHtml,
  rotation,
  background,
  zIndex,
  offset,
  width,
  height,
}: PostcardProps) {
  return (
    <div
      className="absolute rounded-lg shadow-2xl transform transition-all duration-500"
      style={{
        background,
        transform: `rotate(${rotation}deg) translate(${offset.x}px, ${offset.y}px)`,
        zIndex: zIndex,
        width: `${width ?? 800}px`,
        height: `${height ?? 500}px`,
      }}
    >
      {/* Lined paper effect */}
      <div className="absolute inset-0 pointer-events-none">
        <div
          className="h-full w-full"
          style={{
            background: `repeating-linear-gradient(0deg, transparent, transparent 31px, rgba(${PAPER_LINE_COLOR}, ${PAPER_LINE_OPACITY}) 31px, rgba(${PAPER_LINE_COLOR}, ${PAPER_LINE_OPACITY}) 32px)`,
          }}
        ></div>
      </div>

      {/* Content area */}
      <div className="relative p-8 h-full flex flex-col justify-center items-center text-center">
        {contentHtml}
      </div>

      {/* Corner fold effect */}
      <div className="absolute top-0 right-0 w-10 h-10 overflow-hidden">
        <div className="absolute top-0 right-0 w-14 h-14 bg-linear-to-br from-gray-700 to-gray-900 rotate-45 translate-x-7 -translate-y-7 shadow-inner"></div>
      </div>

      {/* Stamp decoration */}
      <Image
        src="icon.svg"
        alt="Stamp"
        width={80}
        height={80}
        className="absolute top-4 left-4 w-16 h-16 object-cover fill-white"
      />
    </div>
  );
}
