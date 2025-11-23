export default function ProcessingState() {
  return (
    <div className="text-center space-y-6">
      <h2 className="text-3xl font-bold">Processing Your Data...</h2>
      <div className="flex justify-center">
        <div className="w-16 h-16 border-4 border-purple-600 border-t-transparent rounded-full animate-spin" />
      </div>
      <p className="text-xl text-white/80">This may take a few moments</p>
    </div>
  );
}
