import NextButton from "@/src/components/layout/NextButton";

interface IntroSlideProps {
  onContinue: () => void;
}

export default function IntroSlide({ onContinue }: IntroSlideProps) {
  return (
    <div className="relative flex flex-col items-center justify-center h-full space-y-8 bg-linear-to-br from-purple-900 to-indigo-900">
      <h1 className="text-7xl font-bold text-white text-center">
        Your GPT Rewind
      </h1>
      <NextButton onClick={onContinue} disabled={false} />
    </div>
  );
}
