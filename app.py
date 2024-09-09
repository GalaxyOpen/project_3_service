from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from yolo_model import detect_objects
from t5_model import summarize_text
from io import BytesIO
import base64
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')

def validate_image_format(image: Image.Image) -> bool:
    return image.format in ["JPEG", "PNG"]

@app.post("/detect/")
async def detect(file: UploadFile = File(...)):
    logger.info("Detect endpoint called.")
    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes))
        
        if not validate_image_format(image):
            return JSONResponse(status_code=400, content={"error": "지원하지 않는 이미지 포맷입니다. JPEG 또는 PNG만 지원됩니다."})
        
        object_detection_image, emotion_detection_image, t5out, gpt2out = detect_objects(image)
        object_detection_base64 = image_to_base64(object_detection_image)
        emotion_detection_base64 = image_to_base64(emotion_detection_image)
        
        return JSONResponse(content={
            "object_detection": object_detection_base64,
            "emotion_detection": emotion_detection_base64,
            "gpt2": t5out,
            "t5": gpt2out
        })
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return JSONResponse(status_code=500, content={"error": "서버 오류가 발생했습니다."})

@app.post("/summarize/")
async def summarize(text: str):
    logger.info("Summarize endpoint called.")
    try:
        summary = summarize_text(text)
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error processing summary: {e}")
        return JSONResponse(status_code=500, content={"error": "서버 오류가 발생했습니다."})
