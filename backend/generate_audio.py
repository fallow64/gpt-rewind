import os
from config import FISH_AUDIO_API_KEY
from config import REFERENCE_ID
from fishaudio import FishAudio
from fishaudio.utils import save





async def transcribe(userID: str, insights: list[str]):
    client = FishAudio(api_key=FISH_AUDIO_API_KEY)
    i = 1
    for text in insights:
        audio = client.tts.convert(text = text, reference_id = REFERENCE_ID)
        # Ensure the directory exists before saving
        output_dir = os.path.join(os.getcwd(), "user", userID, "sound")
        os.makedirs(output_dir, exist_ok=True)
        save(audio, os.path.join(output_dir, f"{i}.mp3"))






