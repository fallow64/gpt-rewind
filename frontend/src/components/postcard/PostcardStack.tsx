import { PostcardStackItem } from "@/src/types";

interface PostcardStackProps {
  postcards: PostcardStackItem[];
  width: number;
  height: number;
  background: string;
}

export default function PostcardStack({
  postcards,
  width,
  height,
  background,
}: PostcardStackProps) {
  return (
    <div
      className="relative"
      style={{ width: `${width}px`, height: `${height}px` }}
    >
      {postcards.map((postcard, index) => (
        <div
          key={index}
          className="absolute rounded-lg shadow-2xl"
          style={{
            background: background,
            transform: `rotate(${postcard.rotation}deg) translate(${postcard.offset.x}px, ${postcard.offset.y}px)`,
            zIndex: index,
            width: `${width}px`,
            height: `${height}px`,
          }}
        />
      ))}
    </div>
  );
}
