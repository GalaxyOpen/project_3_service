fastapi 백엔드

```bash
conda create -n project3_front python=3.11
```

```bash
conda activate project3_front
```

```bash
우리가 가진 파일 중에 faster_rcnn.py 맨 위에 이와 같은 구문 허용
import os
# OpenMP 비활성화 설정 (중복 로딩 허용)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
```

# faster rcnn을 위한 detectron2 설치
```bash
혹시 numpy 문제가 발생하면 가상환경에서 numpy를 다운그레이드 해볼 것
conda install numpy=1.24.3 
```

Window에서 설치했을 때, Error 발생시
```bash
pyproject.toml 파일을 setup.py가 있는 경로에 만들고 다음 내용 추가
[build-system]
requires = ["setuptools>=64", "wheel", "torch", "torchvision"]
build-backend = "setuptools.build_meta"
```

```bash
pip install -r requirements.txt

1. git clone https://github.com/facebookresearch/detectron2.git
python -m pip install -e detectron2 

or 
2. 에러 발생 시
pip install -r requirements.txt
git clone https://github.com/facebookresearch/detectron2.git
cd detectron 
python -m pip install -e . --use-pep517

```

```bash
uvicorn main:app --host 0.0.0.0 --port 1234 --reload
```

streamlit 프론트 엔드
```bash
streamlit run app.py
```

sql 구문 대비
```bash
sql.sql
```
# 결과 이미지
![front_image](front_image.png)

