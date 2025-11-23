import os
from config import FISH_AUDIO_API_KEY
from config import REFERENCE_ID
from fishaudio import FishAudio
from fishaudio.utils import save


# insights.json file is gonna have to have 
# a) the thing to say
# b) the index


async def transcribe(userID: str, insights: list[str]):
    client = FishAudio(api_key=FISH_AUDIO_API_KEY)
    i = 1
    for text in insights:
        audio = client.tts.convert(text = text, reference_id = REFERENCE_ID)
        # Ensure the directory exists before saving
        output_dir = os.path.join(os.getcwd(), "user", userID, "sound")
        os.makedirs(output_dir, exist_ok=True)
        save(audio, os.path.join(output_dir, f"{i}.mp3"))


async def getSoundFile(userID: str, slideID: int):
    """
    Constructs the path to a user's sound file and checks if it exists.

    Args:
        userID: The ID of the user.
        slideID: The index of the sound file (corresponds to 'i' in transcribe).

    Returns:
        The full path to the MP3 file if it exists, otherwise None.
    """
    file_path = os.path.join(os.getcwd(), "user", userID, "sound", f"{slideID}.mp3")
    
    if os.path.exists(file_path):
        return file_path
    else:
        return None





