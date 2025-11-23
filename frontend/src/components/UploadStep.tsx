"use client";

import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

interface UploadStepProps {
  onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  isUploading: boolean;
}

export default function UploadStep({
  onFileUpload,
  isUploading,
}: UploadStepProps) {
  const [showInstructions, setShowInstructions] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (isUploading) {
    return (
      <div className="text-center space-y-6 w-full">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500"></div>
        </div>
        <h2 className="text-3xl font-bold">Processing Your Data...</h2>
        <p className="text-xl text-white/80">
          This may take a moment. Please don't close this page.
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="text-center space-y-6 w-full">
        <h2 className="text-3xl font-bold">Upload Your Data</h2>
        <p className="text-xl text-white/80">
          Upload your ChatGPT conversation data (JSON format)
        </p>
        <button
          onClick={() => setShowInstructions(true)}
          className="text-purple-300 hover:text-purple-200 underline text-sm transition-colors"
        >
          Don't have your data? Click here for instructions
        </button>
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

      {/* Instructions Modal */}
      {mounted &&
        showInstructions &&
        createPortal(
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 max-w-3xl max-h-[90vh] overflow-y-auto shadow-2xl">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-3xl font-bold text-white">
                  How to Get Your ChatGPT Data
                </h3>
                <button
                  onClick={() => setShowInstructions(false)}
                  className="text-white/60 hover:text-white text-4xl leading-none transition-colors"
                >
                  ×
                </button>
              </div>

              <div className="space-y-8 text-white/90">
                {/* Step 1: Request Data */}
                <div>
                  <h4 className="text-xl font-semibold text-purple-300 mb-4">
                    Step 1: Request Your Data from OpenAI
                  </h4>
                  <ol className="space-y-3 list-decimal list-inside">
                    <li>
                      Visit{" "}
                      <a
                        href="https://privacy.openai.com/policies"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-400 hover:text-purple-300 underline"
                      >
                        https://privacy.openai.com/policies
                      </a>
                    </li>
                    <li>
                      Verify your ChatGPT account using your email address
                    </li>
                    <li>
                      Click on "I would like to download my data" and enter the
                      required details
                    </li>
                    <li>
                      Check your email for a confirmation link from OpenAI and
                      open it
                    </li>
                    <li>Enter your country when prompted</li>
                    <li>
                      Wait approximately 30 minutes for your data to be prepared
                      (this time may vary)
                    </li>
                  </ol>
                </div>

                {/* Step 2: Extract File */}
                <div>
                  <h4 className="text-xl font-semibold text-purple-300 mb-4">
                    Step 2: Extract the Conversations File
                  </h4>
                  <ol className="space-y-3 list-decimal list-inside">
                    <li>Unzip the downloaded archive</li>
                    <li>
                      Navigate to{" "}
                      <code className="bg-purple-900/50 px-2 py-1 rounded text-sm">
                        User Online
                        Activity/personal/conversations/conversations.json
                      </code>
                    </li>
                    <li>Use this file when uploading your data above</li>
                  </ol>
                </div>

                <div className="pt-4 border-t border-purple-500/30">
                  <p className="text-sm text-white/60">
                    Note: Your data is processed locally and securely. We
                    temporarily handle the data for processing, but it is never
                    stored permanently or shared with third parties.
                  </p>
                </div>
              </div>

              <div className="mt-8 text-center">
                <button
                  onClick={() => setShowInstructions(false)}
                  className="px-8 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors"
                >
                  Got it!
                </button>
              </div>
            </div>
          </div>,
          document.body
        )}
    </>
  );
}
