from fastapi import FastAPI, Request, UploadFile, File
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from typing import List
import numpy as np
import cv2
import PIL
from predict_services import predict, ImagePredict
from cv2_services import draw_text
from S3_services import upload_object

app = FastAPI()
templates = Jinja2Templates("templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def inference(files: List[UploadFile] = File()):
    img_predicts = await predict(files)
    images = []
    for img_predict, img in zip(img_predicts, files):
        img_extension = img.filename.split(".")[-1]
        file_key = f'{uuid4()}.{img_extension}'
        image = np.asarray(bytearray(img_predict.original_image), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        for box in img_predict.bboxes:
            cv2.rectangle(image, box.left_top, box.right_bottom, (0, 0, 255), 2)
            draw_text(image, f"{box.box_class} {box.conf:.2f}", pos=(box.left_top[0], box.right_bottom[1]))
        image_as_bytes = cv2.imencode(f".{img_extension}", image)[1].tobytes()
        img_predict.link_to_processed_image = await upload_object(file_key, image_as_bytes)
        img_predict.original_image = None
        images.append(img_predict)
    return images


@app.post("/inference-template")
async def inference_to_template(files: List[UploadFile] = File()):
    try:
        images = await inference(files)
    except PIL.UnidentifiedImageError:
        return templates.TemplateResponse("index.html", {"request": {}, "error": "Вы загрузили не изображение!"})
    return templates.TemplateResponse("index.html", {"request": {}, "images": images})


@app.post("/inference-json")
async def inference_to_json(files: List[UploadFile] = File()) -> List[ImagePredict] | dict:
    try:
        results = await inference(files)
    except PIL.UnidentifiedImageError:
        return {"error": "Вы загрузили не изображения!"}
    return results
