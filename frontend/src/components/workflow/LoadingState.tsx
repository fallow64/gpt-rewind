export default function LoadingState() {
  return (
    <div className="text-center space-y-6">
      <div className="flex justify-center">
        <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
      </div>
      <p className="text-xl text-white/80">Loading...</p>
    </div>
  );
}
