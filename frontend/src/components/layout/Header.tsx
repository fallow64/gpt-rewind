import AuthSection from "../auth/AuthSection";

function Header() {
  return (
    <div className="w-full bg-gray-800 text-white text-2xl flex items-center justify-between">
      <div
        className="font-bold p-4"
        style={{
          fontFamily: "'Georgia', 'Times New Roman', serif",
          fontStyle: "italic",
        }}
      >
        GPT Rewind
      </div>

      <div className="flex items-center gap-6 mr-4">
        <div className="text-sm">
          <span>made with &lt;3 for MadHacks 2025</span> <br />
          <span className="ml-4">by Albert, Austin, and Geet</span>
        </div>

        <AuthSection />
      </div>
    </div>
  );
}

export default Header;
