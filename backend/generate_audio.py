import os
from config import FISH_AUDIO_API_KEY
from config import REFERENCE_ID
from fishaudio.client import FishAudio
from fishaudio.utils import save

async def transcribe_insight(user_id: str, insight: object, page_index: int):
    match page_index:
        case -1:
            # intro
            text = "Hey, it's your favorite AI company CEO. Welcome to GPT Rewind! Let's take a look at what you have here..."
        case 0:
            # total hours
            text = "Here's the total amount of time you spent on GPT this year. Hopefully you used that time wisely. But if you didn't... don't worry. Your secret is safe with us."
        case 1:
            # total hours by month
            text = "And here's the amount of hours you spent grouped by month. Looks like [month] was your biggest month!"
        case 2:
            # total hours grouped by hour/frequency of hours
            text = "Let's take a look at what times of the day you used GPT the most."
        case 3:
            # longest conversation duration
            text = "Here's the longest time you spent conversing with GPT. [hour] hours! I wonder what you were doing then."
        case 4:
            # easiest question
            text = "Here's the easiest question you asked this year. Don't worry, we all have that moment sometimes."
        case 5:
            # hardest question
            text = "And here's the hardest question you asked."
        case 6:
            # profession
            text = "Based on your data, here's what we think what field you work in."
        case 7:
            # top 3 topics
            text = "Let's take a look at the top 3 topics you searched up this past year."
        case 8:
            # topics per month
            text = "Here's how what you've looked up on GPT has changed over the months."
        case 9:
            # topics per hour 
            text = "And here's what topics you've looked up at each hour of the day."
        case 10:
            # outro
            text = "Placeholder."
        case _:
            # Default case for any other page_index
            return None
    
    await transcribe_literal(user_id=user_id, text=text, page_index=page_index)
    return text


async def transcribe_literal(user_id: str, text: str, page_index: int):
    client = FishAudio(api_key=FISH_AUDIO_API_KEY)
    audio = client.tts.convert(text = text, reference_id = REFERENCE_ID)
    output_dir = os.path.join("output_files", user_id, "sounds")
    os.makedirs(output_dir, exist_ok=True)
    save(audio, os.path.join(output_dir, f"{page_index}.mp3"))
