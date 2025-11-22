interface BackButtonProps {
  onClick: () => void;
  disabled: boolean;
}

export default function BackButton({ onClick, disabled }: BackButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="absolute bottom-8 left-8 px-6 py-3 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 text-white font-semibold rounded-lg shadow-lg transition-all duration-200 hover:scale-105 disabled:cursor-not-allowed disabled:hover:scale-100 z-200"
    >
      ← Back
    </button>
  );
}
