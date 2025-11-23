"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useConversation } from "@/src/contexts/ConversationContext";
import ProgressIndicator from "@/src/components/workflow/ProgressIndicator";
import StepLabels from "@/src/components/workflow/StepLabels";
import UploadStep from "@/src/components/workflow/UploadStep";
import ProcessStep from "@/src/components/workflow/ProcessStep";
import ProcessingState from "@/src/components/workflow/ProcessingState";
import LoadingState from "@/src/components/workflow/LoadingState";

export default function Home() {
  const router = useRouter();
  const { setConversationId } = useConversation();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);

  const stepLabels = ["Sign In", "Upload", "Process", "View Insights"];

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === "application/json") {
      setUploadedFile(file);
      setCurrentStep(3);
    } else {
      alert("Please upload a valid JSON file");
    }
  };

  const handleProcessData = async () => {
    if (!uploadedFile) return;

    setIsProcessing(true);

    try {
      // Create FormData to upload the file
      const formData = new FormData();
      formData.append("file", uploadedFile);

      // Upload to backend
      const response = await fetch("http://localhost:8000/conversation", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to upload conversation data");
      }

      const result = await response.json();
      const conversationId = result.conversationId;

      if (!conversationId) {
        throw new Error("No conversation ID returned from server");
      }

      // Store conversation ID in context
      setConversationId(conversationId);

      // Redirect to insights
      router.push("/insights");
    } catch (error) {
      console.error("Error processing data:", error);
      alert("Failed to process data. Please try again.");
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-linear-to-br from-gray-950 via-gray-900 to-black text-white p-8">
      <div className="max-w-4xl mx-auto w-full space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-6xl font-bold">Welcome to GPT Rewind</h1>
          <p className="text-2xl text-white/80">
            Discover your ChatGPT conversation insights
          </p>
        </div>

        <ProgressIndicator currentStep={currentStep} totalSteps={3} />

        {/* Step Content */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 min-h-[300px] flex flex-col items-center justify-center">
          {/* Step 1: Upload */}
          {currentStep === 1 && !uploadedFile && (
            <UploadStep onFileUpload={handleFileUpload} />
          )}

          {/* Step 2: Process */}
          {currentStep === 2 && !isProcessing && uploadedFile && (
            <ProcessStep
              fileName={uploadedFile.name}
              onChangeFile={() => {
                setUploadedFile(null);
                setCurrentStep(2);
              }}
              onProcess={handleProcessData}
            />
          )}

          {/* Processing State */}
          {isProcessing && <ProcessingState />}
        </div>

        <StepLabels currentStep={currentStep} steps={stepLabels} />
      </div>
    </div>
  );
}
