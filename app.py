# app.py
import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import base64
from loguru import logger
import time

st.sidebar.title("AI 모델을 활용한 객체 탐지 및 감정 분석")

# YOLO 섹션
st.sidebar.header("무플 방지 위원회")

st.sidebar.header("옵션 설정")
uploaded_file = st.sidebar.file_uploader("이미지를 업로드하세요", type=["jpg", "jpeg", "png"])

object_detect_option = st.sidebar.selectbox("얼굴 표정 검출 모델을 선택하세요", ["yolov10n", "faster_rcnn"])
language_model_option = st.sidebar.selectbox("언어 모델을 선택하세요", ["t5_base", "t5_large", "gpt2", "kogpt2"])

object_detect_endpoint = f"http://127.0.0.1:1234/{object_detect_option}"



if uploaded_file is not None:
    
    time_ = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    logger.add(f"result_front/{time_}/{object_detect_option}_{language_model_option}.log", format="{message}", level="INFO")

    # 바이트로 변환
    image_bytes = uploaded_file.read()
    
    # 입력 이미지 출력
    st.subheader("입력 이미지")
    st.image(
        uploaded_file,
        caption="입력 이미지",
        use_column_width=True,
        channels="RGB"  # 이미지가 RGB 채널을 사용하는 경우
    )
    
    # 파일 객체 요청
    files = {"file": ("image.png", image_bytes, "image/png")}
    data = {"lm_opt": language_model_option}
    
    # FastAPI 에게 요청
    response = requests.post(object_detect_endpoint, files=files, data=data)
    
    if response.status_code == 200:
        response_data = response.json()
        
        # 응답 데이터의 키를 안전하게 처리
        object_detection_base64 = response_data.get("object_detection_image", "No object detection image")
        emotion_detection_base64 = response_data.get("emotion_detection_image", "No emotion detection image")
        pred_label = response_data.get("pred_label", "No label")
        lm_out = response_data.get("lm_out", "No output")
        
        # Base64를 이미지로 디코딩
        if object_detection_base64 != "No object detection image":
            object_detection_image = Image.open(BytesIO(base64.b64decode(object_detection_base64)))
        else:
            object_detection_image = None
        
        if emotion_detection_base64 != "No emotion detection image":
            emotion_detection_image = Image.open(BytesIO(base64.b64decode(emotion_detection_base64)))
        else:
            emotion_detection_image = None
        
        # 라벨 출력
        st.sidebar.write(f"감정 및 객체 감지: {pred_label}")

        st.sidebar.subheader("Emotion Detection Results")
        if object_detection_image:
            st.sidebar.image(
                object_detection_image,
                caption="Object Detection Result",
                use_column_width=True,
                channels="RGB"  # 이미지가 RGB 채널을 사용하는 경우
            )
        else:
            st.sidebar.write("No object detection image available.")
        
        # Emotion Detection 결과 출력
        st.sidebar.subheader("Object Detection Results")
        if emotion_detection_image:
            st.sidebar.image(
                emotion_detection_image,
                caption="Emotion Detection Result",
                use_column_width=True,
                channels="RGB"  # 이미지가 RGB 채널을 사용하는 경우
            )
        else:
            st.sidebar.write("No emotion detection image available.")
        
        # lm_out 출력
        st.subheader(f"{language_model_option} 의 댓글")
        if "출력값" in lm_out:
            out_text = lm_out.split("출력값: ")[-1]
        else:
            out_text = lm_out
        
        st.markdown(f"<h2 style='font-size:32px;'>{out_text}</h2>", unsafe_allow_html=True)
        
        logger.info(f"model:{object_detect_option}, lm:{language_model_option}, result:{pred_label}, out_text:{out_text}")
    else:
        st.error(f"Error: {response.text}")
    
    logger.remove()
