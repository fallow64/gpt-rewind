from config import FISH_AUDIO_API_KEY
from config import REFERENCE_ID
from fishaudio import FishAudio
from fishaudio.utils import save





def put_audios(array_of_text):
    client = FishAudio(api_key=FISH_AUDIO_API_KEY)
    # backend will give me an array of things to say
    list_of_filenames = []
    i = 1
    for text in array_of_text:
        audio = client.tts.convert(
            text=text,
            reference_id=REFERENCE_ID
        )
    save(audio, "/files{i}.mp3") # type: ignore
    list_of_filenames.append("/files{i}.mp3")
    




