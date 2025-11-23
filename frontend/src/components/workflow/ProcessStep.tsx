interface ProcessStepProps {
  fileName: string;
  onChangeFile: () => void;
  onProcess: () => void;
}

export default function ProcessStep({
  fileName,
  onChangeFile,
  onProcess,
}: ProcessStepProps) {
  return (
    <div className="text-center space-y-6">
      <h2 className="text-3xl font-bold">Step 3: Process Your Data</h2>
      <p className="text-xl text-white/80">
        File uploaded: <span className="font-mono">{fileName}</span>
      </p>
      <div className="flex gap-4 justify-center mt-8">
        <button
          onClick={onChangeFile}
          className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition-colors"
        >
          Choose Different File
        </button>
        <button
          onClick={onProcess}
          className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors"
        >
          Process Data
        </button>
      </div>
    </div>
  );
}
