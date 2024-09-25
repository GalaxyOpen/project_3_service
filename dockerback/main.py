# main.py
from fastapi import FastAPI, File, UploadFile, Form, HTTPException # HTTPException 추가 
from fastapi.responses import JSONResponse
from PIL import Image
import io
import base64
from py_model import yolo10n_face, yolo_oiv, faster_rcnn, gpt2, kogpt2, t5_base, t5_large
import time

from loguru import logger
import mysql.connector  # MySQL을 사용하기 위한 추가

app = FastAPI()

# MySQL 연결 설정 : DB 연결 함수
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="ai_third",
        password="1234",
        database="db_ai_third"
    )
    return conn
    

def language_model_out(prompt, lm_opt):
    if lm_opt == "gpt2":
        return gpt2.gentext(prompt)
    elif lm_opt == "kogpt2":
        return kogpt2.gentext(prompt)
    elif lm_opt == "t5_base":
        return t5_base.gentext(prompt)
    elif lm_opt == "t5_large":
        return t5_large.gentext(prompt)
    else:
        return "Not Implemented"

@app.post("/yolov10n")
async def yolov10n_endpoint(file: UploadFile = File(...), lm_opt: str = Form(...)):
# 이미지 읽기 -> 객체 및 감정 탐지 -> 
    time_ = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    # 로거 생성
    logger.add(f"result/{time_}/yolo_v10_face_{lm_opt}.log", format="{message}", level="INFO")
    
    # 이미지 파일 읽기
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    
    # 이미지 처리(객체 및 감정 탐지 수행)
    object_detection_numpy, pred_face = yolo10n_face.yolo_v10_face_out(image)
    emotion_detection_numpy, pred_obj = yolo_oiv.yolo_oiv_out(image)
    pred_face.append(pred_obj)
    result_string = f"{pred_face}"
    
    # reshape : rgb to bgr 변경(이미지 변환 및 저장 준비1)
    object_detection_numpy = object_detection_numpy[:, :, ::-1]
    emotion_detection_numpy = emotion_detection_numpy[:, :, ::-1]
    
    # numpy to image(이미지 변환 및 저장 준비2)
    object_detection_image = Image.fromarray(object_detection_numpy)
    emotion_detection_image = Image.fromarray(emotion_detection_numpy)
    
    # image to byte : 이미지 -> 바이트 변환
    # with io.BytesIO() as buffer:
    #     object_detection_image.save(buffer, format='PNG')
    #     object_detection_image_byte = buffer.getvalue()
        
    # with io.BytesIO() as buffer:
    #     emotion_detection_image.save(buffer, format='PNG')
    #     emotion_detection_image_byte = buffer.getvalue()

    # image to base64 (+이미지가 None이 아닌 경우에만 base64로 변환)
    object_detection_base64 = None
    emotion_detection_base64 = None
    
    if object_detection_image:
        with io.BytesIO() as buffer:
            object_detection_image.save(buffer, format='PNG')
            object_detection_image_byte = buffer.getvalue()
            object_detection_base64 = base64.b64encode(object_detection_image_byte).decode('utf-8')

    if emotion_detection_image:
        with io.BytesIO() as buffer:
            emotion_detection_image.save(buffer, format='PNG')
            emotion_detection_image_byte = buffer.getvalue()
            emotion_detection_base64 = base64.b64encode(emotion_detection_image_byte).decode('utf-8')

    
    # 언어 모델을 통한 댓글 생성
    lm_out = language_model_out(result_string, lm_opt)

    # MySQL에 댓글 저장
    conn = None
    cursor = None 
    try: 
        conn = get_db_connection() # DB 연결
        cursor = conn.cursor() # 커서 생성 
        sql_insert = "INSERT INTO comments (comment_text) VALUES (%s)"
        cursor.execute(sql_insert, (lm_out,))  # SQL 실행
        conn.commit() # 변경 사항 커밋
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) # 에러 발생 시 예외 처리
    finally:
        if cursor is not None and hasattr(cursor, "close"): 
            cursor.close()
        if conn is not None and hasattr(conn, "close"):
            conn.close()    
    
    # JSON 응답 반환
    response_content = {
        "pred_label": result_string,
        "lm_out": lm_out
    }
    # 안전하게 반환: 이미지를 처리할 수 없으면 이 값을 넣지 않음
    if object_detection_base64:
        response_content["object_detection_image"] = object_detection_base64
    else:
        response_content["object_detection_image"] = "No object detection image"

    if emotion_detection_base64:
        response_content["emotion_detection_image"] = emotion_detection_base64
    else:
        response_content["emotion_detection_image"] = "No emotion detection image"

    return JSONResponse(content=response_content)

# faster_rcnn
@app.post("/faster_rcnn")
async def yolov10n_endpoint(file: UploadFile = File(...), lm_opt: str = Form(...)):
    time_ = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    # 로거 생성
    logger.add(f"result/{time_}/yolo_v10_face_{lm_opt}.log", format="{message}", level="INFO")
    
    # 이미지 파일 읽기
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    
    # 이미지 처리 : 객체 및 감정 탐지 수행
    object_detection_numpy, pred_face = faster_rcnn.rcnn_out(image)
    emotion_detection_numpy, pred_obj = yolo_oiv.yolo_oiv_out(image)
    pred_face.append(pred_obj)
    result_string = f"{pred_face}"
    
    # transepose rgb to bgr 변경
    emotion_detection_numpy = emotion_detection_numpy[:, :, ::-1]
    
    # numpy to image
    object_detection_image = Image.fromarray(object_detection_numpy)
    emotion_detection_image = Image.fromarray(emotion_detection_numpy)
    
    # image to byte
    with io.BytesIO() as buffer:
        object_detection_image.save(buffer, format='PNG')
        object_detection_image_byte = buffer.getvalue()
        
    with io.BytesIO() as buffer:
        emotion_detection_image.save(buffer, format='PNG')
        emotion_detection_image_byte = buffer.getvalue()

    # image to base64
    with io.BytesIO() as buffer:
        object_detection_image.save(buffer, format='PNG')
        object_detection_image_byte = buffer.getvalue()
        object_detection_base64 = base64.b64encode(object_detection_image_byte).decode('utf-8')

    with io.BytesIO() as buffer:
        emotion_detection_image.save(buffer, format='PNG')
        emotion_detection_image_byte = buffer.getvalue()
        emotion_detection_base64 = base64.b64encode(emotion_detection_image_byte).decode('utf-8')
    
    # 언어 모델을 통한 댓글 생성
    lm_out = language_model_out(result_string, lm_opt)
    
    # MysQL에 댓글 저장
    conn = None
    cursor = None 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql_insert = "INSERT INTO comments (comment_text) VALUES (%s)"
        cursor.execute(sql_insert, (lm_out,))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:    
            conn.close()

    # JSON 응답 반환
    return JSONResponse(content={
        "object_detection_image": object_detection_base64,
        "emotion_detection_image": emotion_detection_base64,
        "pred_label": result_string,
        "lm_out": lm_out
    })