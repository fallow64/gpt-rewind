import base64
import os
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from generate_audio import transcribe_insight

OUTPUT_FOLDER = "output_files"
INPUT_FOLDER = "input_files"
app = FastAPI()


# placeholder for albert's function
async def create_analyze_files(output_file_folder: str, conversation_file_path: str):
    # for now just write empty json 0 to 10
    insights_folder = os.path.join(output_file_folder, "insights")
    os.makedirs(insights_folder, exist_ok=True)
    for page_index in range(-1, 11):
        insight_file_path = os.path.join(insights_folder, f"{page_index}.json")
        with open(insight_file_path, "w") as f:
            f.write("{}")


@app.post("/conversation")
async def process_conversation(file: UploadFile = File(...)):
    random_id = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')

    # create user folder
    output_user_folder = os.path.join(OUTPUT_FOLDER, random_id)
    os.makedirs(output_user_folder, exist_ok=True)

    # put uploaded file into input folder
    input_user_folder = os.path.join(INPUT_FOLDER, random_id)
    os.makedirs(input_user_folder, exist_ok=True)
    input_file_path = os.path.join(input_user_folder, random_id)
    with open(input_file_path, "wb") as f:
        f.write(file.file.read())

    # process conversation file
    await create_analyze_files(output_user_folder, input_file_path)

    # read the resulting file and generate audio files
    for page_index in range(-1, 11):
        insight_file_path = os.path.join(output_user_folder, "insights", f"{page_index}.json")
        if os.path.exists(insight_file_path):
            with open(insight_file_path, "r") as f:
                insight_data = f.read()
            await transcribe_insight(user_id=random_id, insight=insight_data, page_index=page_index)


# get json file
# run albert's data stripping and tokenization
@app.get("/data/{random_id}/insights/{page_index}")
async def get_insights_for_page(random_id, page_index):
    # find the file
    file_path = os.path.join(OUTPUT_FOLDER, random_id, "insights", f"{page_index}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = f.read()
        return data
    else:
        # couldn't find the file, 404
        raise HTTPException(status_code=404, detail="Item not found")
    
    

@app.get("/data/{random_id}/sounds/{page_index}")
async def get_sound_for_page(random_id: str, page_index: int):
    file_path = os.path.join(OUTPUT_FOLDER, random_id, "sound", f"{page_index}.mp3")
    
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_path)
    else:
        raise HTTPException(status_code=404, detail="Item not found")
