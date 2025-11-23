"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import ProgressIndicator from "@/src/components/workflow/ProgressIndicator";
import StepLabels from "@/src/components/workflow/StepLabels";
import SignInStep from "@/src/components/workflow/SignInStep";
import UploadStep from "@/src/components/workflow/UploadStep";
import ProcessStep from "@/src/components/workflow/ProcessStep";
import ProcessingState from "@/src/components/workflow/ProcessingState";
import LoadingState from "@/src/components/workflow/LoadingState";
import { useData } from "@/src/contexts/DataContext";

export default function Home() {
  const { data: session, status } = useSession();
  const router = useRouter();
  const { setUploadedData } = useData();
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
      // Read file content
      const fileContent = await uploadedFile.text();
      const jsonData = JSON.parse(fileContent);

      // Store data in context for use across the app
      setUploadedData(jsonData);

      // Generic POST API call - easy to edit
      const response = await fetch("/api/process-data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId: session?.user?.id,
          data: jsonData,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to process data");
      }

      const result = await response.json();
      console.log("Processing result:", result);

      // Redirect to insights
      router.push("/insights");
    } catch (error) {
      console.error("Error processing data:", error);
      alert("Failed to process data. Please try again.");
      setIsProcessing(false);
    }
  };

  // Update step based on authentication
  if (status === "authenticated" && currentStep === 1) {
    setCurrentStep(2);
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-linear-to-br from-gray-950 via-gray-900 to-black text-white p-8">
      <div className="max-w-4xl mx-auto w-full space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-6xl font-bold">Welcome to GPT Rewind</h1>
          <p className="text-2xl text-white/80">
            Discover your ChatGPT conversation insights
          </p>
        </div>

        <ProgressIndicator currentStep={currentStep} totalSteps={4} />

        {/* Step Content */}
        <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 min-h-[300px] flex flex-col items-center justify-center">
          {/* Step 1: Login */}
          {currentStep === 1 && <SignInStep />}

          {/* Step 2: Upload */}
          {currentStep === 2 && !uploadedFile && (
            <UploadStep onFileUpload={handleFileUpload} />
          )}

          {/* Step 3: Process */}
          {currentStep === 3 && !isProcessing && uploadedFile && (
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

          {/* Loading state for initial auth check */}
          {status === "loading" && <LoadingState />}
        </div>

        <StepLabels currentStep={currentStep} steps={stepLabels} />
      </div>
    </div>
  );
}
