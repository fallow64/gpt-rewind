interface NextButtonProps {
  onClick: () => void;
  disabled: boolean;
}

export default function NextButton({ onClick, disabled }: NextButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="absolute bottom-8 right-8 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-semibold rounded-lg shadow-lg transition-all duration-200 hover:scale-105 disabled:cursor-not-allowed disabled:hover:scale-100 z-200"
    >
      Next →
    </button>
  );
}
