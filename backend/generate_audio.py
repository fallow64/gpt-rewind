import os
from config import FISH_AUDIO_API_KEY
from config import REFERENCE_ID
from fishaudio import FishAudio
from fishaudio.utils import save


async def transcribe(userID: str, insight: str, insightID: int):
    client = FishAudio(api_key=FISH_AUDIO_API_KEY)
    audio = client.tts.convert(text = insight, reference_id = REFERENCE_ID)
    output_dir = os.path.join(os.getcwd(), "user", userID, "sound")
    os.makedirs(output_dir, exist_ok=True)
    save(audio, os.path.join(output_dir, f"{insightID}.mp3"))







