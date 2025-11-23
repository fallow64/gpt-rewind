import Image from "next/image";
import Link from "next/link";

function Header() {
  return (
    <div className="w-full bg-gray-800 text-white text-2xl flex items-center justify-between">
      <Link
        href="/"
        className="font-bold m-4 hover:text-purple-300 transition-colors cursor-pointer flex items-center"
        style={{
          fontFamily: "'Georgia', 'Times New Roman', serif",
          fontStyle: "italic",
        }}
      >
        GPT Rewind
        <Image
          src="/repeat.svg"
          alt="Repeat icon"
          width={32}
          height={32}
          className="invert"
        />
      </Link>

      <div className="flex items-center gap-6 mr-4">
        <div className="text-sm">
          <span>
            made with <span className="text-red-300">{"<3"}</span> for{" "}
            <Link
              className="italic cursor-pointer underline"
              href="https://madhacks.io"
              target="_blank"
            >
              MadHacks 2025
            </Link>
          </span>
          <br />
          <span className="ml-4">by Albert, Austin, and Geet</span>
        </div>
      </div>
    </div>
  );
}

export default Header;
