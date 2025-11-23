import asyncio
import base64
import json
import os
import logging
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from generate_audio import transcribe_insight
from ml.pipeline import run_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_FOLDER = "output_files"
INPUT_FOLDER = "input_files"
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def create_analyze_files(output_file_folder: str, conversation_file_path: str, random_id: str):
    """
    Process conversation file through ML pipeline and generate insights.
    
    Args:
        output_file_folder: Directory for output files
        conversation_file_path: Path to uploaded conversation JSON file
        random_id: User ID for this session
    """
    try:
        logger.info(f"Starting ML pipeline for user {random_id}")
        
        # Run the ML pipeline
        # Note: Embeddings and analytics are disabled by default for speed
        # They can be enabled but require GPU and significant processing time
        result = run_pipeline(
            conversation_file=conversation_file_path,
            output_dir=output_file_folder,
            enable_embeddings=False,  # Set to True to enable (requires GPU, slow)
            enable_analytics=False     # Set to True to enable (requires embeddings)
        )
        
        if not result['success']:
            logger.error(f"Pipeline failed for user {random_id}: {result['error']}")
            # Create fallback empty insights
            insights_folder = os.path.join(output_file_folder, "insights")
            os.makedirs(insights_folder, exist_ok=True)
            for page_index in range(-1, 11):
                insight_file_path = os.path.join(insights_folder, f"{page_index}.json")
                with open(insight_file_path, "w") as f:
                    f.write('{"error": "Processing failed"}')
            return
        
        logger.info(f"Pipeline completed successfully for user {random_id}")
        
        # Generate audio for insights (optional - currently disabled in original code)
        # Uncomment to enable audio generation
        """
        insights_folder = os.path.join(output_file_folder, "insights")
        for page_index in range(-1, 11):
            insight_file_path = os.path.join(insights_folder, f"{page_index}.json")
            if os.path.exists(insight_file_path):
                with open(insight_file_path, "r") as f:
                    insight_data = f.read()
                await transcribe_insight(user_id=random_id, insight=insight_data, page_index=page_index)
        """
        
    except Exception as e:
        logger.exception(f"Error processing conversation for user {random_id}: {e}")
        # Create error insights
        insights_folder = os.path.join(output_file_folder, "insights")
        os.makedirs(insights_folder, exist_ok=True)
        for page_index in range(-1, 11):
            insight_file_path = os.path.join(insights_folder, f"{page_index}.json")
            with open(insight_file_path, "w") as f:
                f.write('{"error": "Processing error"}')


@app.post("/conversation")
async def process_conversation(file: UploadFile = File(...)):
    # random_id = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
    random_id = "abc"

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
    asyncio.create_task(create_analyze_files(output_user_folder, input_file_path, random_id))
    
    # Return the conversation ID
    return {"conversationId": random_id}


# get json file
# run albert's data stripping and tokenization
@app.get("/data/{random_id}/insights/{page_index}")
async def get_insights_for_page(random_id, page_index):
    # find the file
    file_path = os.path.join(OUTPUT_FOLDER, random_id, "insights", f"{page_index}.json")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)  # Parse JSON instead of reading as string
        return data
    else:
        # couldn't find the file, 404
        raise HTTPException(status_code=404, detail="Insight not found")
    
    

@app.get("/data/{random_id}/sounds/{page_index}")
async def get_sound_for_page(random_id: str, page_index: int):
    file_path = os.path.join(OUTPUT_FOLDER, random_id, "sounds", f"{page_index}.mp3")
    print(f"Looking for sound file at: {file_path}")
    
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_path)
    else:
        raise HTTPException(status_code=404, detail="Sound not found")
