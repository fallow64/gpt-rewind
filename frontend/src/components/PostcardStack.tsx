import Postcard from "./Postcard";
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
        <Postcard
          key={index}
          background={background}
          rotation={postcard.rotation}
          zIndex={index}
          offset={postcard.offset}
          width={width}
          height={height}
        />
      ))}
    </div>
  );
}
