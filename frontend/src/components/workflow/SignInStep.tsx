import AuthSection from "@/src/components/auth/AuthSection";

export default function SignInStep() {
  return (
    <div className="text-center space-y-6">
      <h2 className="text-3xl font-bold">Step 1: Sign In</h2>
      <p className="text-xl text-white/80">
        Choose your preferred authentication method
      </p>
      <div className="flex justify-center mt-6">
        <AuthSection />
      </div>
    </div>
  );
}
