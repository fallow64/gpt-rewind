interface ProgressIndicatorProps {
  currentStep: number;
  totalSteps?: number;
}

export default function ProgressIndicator({
  currentStep,
  totalSteps = 4,
}: ProgressIndicatorProps) {
  return (
    <div className="flex justify-center items-center space-x-4 my-12">
      {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step) => (
        <div key={step} className="flex items-center">
          <div
            className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg border-2 transition-all ${
              step <= currentStep
                ? "bg-purple-600 border-purple-400 text-white"
                : "bg-gray-800 border-gray-600 text-gray-400"
            }`}
          >
            {step}
          </div>
          {step < totalSteps && (
            <div
              className={`w-16 h-1 transition-all ${
                step < currentStep ? "bg-purple-600" : "bg-gray-700"
              }`}
            />
          )}
        </div>
      ))}
    </div>
  );
}
