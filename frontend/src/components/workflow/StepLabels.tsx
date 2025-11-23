interface StepLabelsProps {
  currentStep: number;
  steps: string[];
}

export default function StepLabels({ currentStep, steps }: StepLabelsProps) {
  return (
    <div className="flex justify-center items-center space-x-4 text-sm text-white/60">
      {steps.map((label, index) => (
        <div key={index} className="flex items-center space-x-4">
          <span className={currentStep >= index + 1 ? "text-white/90" : ""}>
            {index + 1}. {label}
          </span>
          {index < steps.length - 1 && <span>→</span>}
        </div>
      ))}
    </div>
  );
}
