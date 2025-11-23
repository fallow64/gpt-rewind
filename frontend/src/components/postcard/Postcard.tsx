import { PostcardProps } from "@/src/types";

export default function Postcard({
  contentHtml,
  rotation,
  zIndex,
  offset,
  width = 800,
  height = 500,
}: PostcardProps) {
  return (
    <div
      className="absolute rounded-lg shadow-2xl transform transition-all duration-500"
      style={{
        transform: `rotate(${rotation}deg) translate(${offset.x}px, ${offset.y}px)`,
        zIndex: zIndex,
        width: `${width}px`,
        height: `${height}px`,
      }}
    >
      {/* Content area */}
      <div
        className="relative h-full w-full"
        style={{
          backgroundColor: "#304158",
        }}
      >
        {contentHtml}
      </div>

      {/* Corner fold effect */}
      <div className="absolute top-0 right-0 w-10 h-10 overflow-hidden">
        <div className="absolute top-0 right-0 w-14 h-14 bg-linear-to-br from-gray-700 to-gray-900 rotate-45 translate-x-7 -translate-y-7 shadow-inner opacity-50"></div>
      </div>

      {/* Stamp decoration */}
      {/* <Image
        src="icon.svg"
        alt="Stamp"
        width={80}
        height={80}
        className="absolute top-4 left-4 w-16 h-16 object-cover fill-green-600"
      /> */}
    </div>
  );
}
