interface UploadStepProps {
  onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function UploadStep({ onFileUpload }: UploadStepProps) {
  return (
    <div className="text-center space-y-6 w-full">
      <h2 className="text-3xl font-bold">Step 2: Upload Your Data</h2>
      <p className="text-xl text-white/80">
        Upload your ChatGPT conversation data (JSON format)
      </p>
      <div className="mt-8">
        <label
          htmlFor="file-upload"
          className="cursor-pointer inline-block px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors text-lg"
        >
          Choose File
        </label>
        <input
          id="file-upload"
          type="file"
          accept=".json"
          onChange={onFileUpload}
          className="hidden"
        />
      </div>
      <p className="text-sm text-white/60 mt-4">
        Your data is processed securely and never stored permanently
      </p>
    </div>
  );
}
