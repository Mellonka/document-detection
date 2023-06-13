from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from uuid import uuid4
from typing import List
from PIL import ImageDraw, Image, ImageFont, UnidentifiedImageError
from services import predict, save_or_upload, draw_text
from schemas import ImagePredict

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'))

templates = Jinja2Templates("templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def inference(files: List[UploadFile] = File()):
    img_predicts = await predict(files)
    annotations = []
    font = ImageFont.truetype('arial.ttf', size=27)
    for img_predict, img_file in zip(img_predicts, files):
        image = Image.open(img_file.file)
        img_format = image.format
        image = image.convert('RGB')
        draw = ImageDraw.Draw(image)
        for box in img_predict.bboxes:
            draw.rectangle((*box.left_top, *box.right_bottom), outline='red', width=3)
            text = f"{box.box_class} {box.conf}"
            x, y = box.left_top[0], box.right_bottom[1]
            draw_text(draw, font, text, x, y)
        img_predict.link_to_processed_image = await save_or_upload(image, img_file.filename, img_format)
        annotations.append(img_predict)
    return annotations


@app.post("/inference-template")
async def inference_to_template(request: Request, files: List[UploadFile] = File()):
    try:
        images = await inference(files)
    except UnidentifiedImageError:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Вы загрузили не изображение!"})
    return templates.TemplateResponse("index.html", {"request": request, "images": images})


@app.post("/inference-json")
async def inference_to_json(files: List[UploadFile] = File()) -> List[ImagePredict] | dict:
    try:
        results = await inference(files)
    except UnidentifiedImageError:
        return {"error": "Вы загрузили не изображения!"}
    return results
