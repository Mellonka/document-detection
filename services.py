from fastapi import UploadFile
from ultralytics import YOLO
from typing import List
from PIL import Image
from schemas import BBox, ImagePredict
from config import AWS_S3_BUCKET_NAME, AWS_SETTINGS
from io import BytesIO
from typing import Union
from uuid import uuid4
import aioboto3


async def predict(files: List[UploadFile]) -> List[ImagePredict]:
    model = YOLO('fast.pt')
    predicts = []
    for file in files:
        img = Image.open(file.file)
        result = model.predict(img, conf=0.20)
        bboxes = []
        for conf, cls, xyxy in zip(result[0].boxes.conf.tolist(), result[0].boxes.cls.tolist(),
                                   result[0].boxes.xyxy.tolist()):
            left_top = (xyxy[0], xyxy[1])
            right_bottom = (xyxy[2], xyxy[3])
            bboxes.append(BBox(left_top=left_top,
                               conf=round(conf, 2),
                               right_bottom=right_bottom,
                               box_class=model.names[cls]))
        predicts.append(ImagePredict(filename=file.filename,
                                     bboxes=bboxes))
    return predicts


async def upload_object(file_key: str, file: Union[UploadFile, bytes, BytesIO]):
    session = aioboto3.Session()
    if type(file) == bytes:
        file = BytesIO(file)
    async with session.client(**AWS_SETTINGS) as s3:
        await s3.upload_fileobj(file, AWS_S3_BUCKET_NAME, file_key)
        return f'https://storage.yandexcloud.net/{AWS_S3_BUCKET_NAME}/{file_key}'


async def save_or_upload(image: Image.Image, img_filename: str, img_format):
    if AWS_S3_BUCKET_NAME is not None:
        img_extension = img_filename.split(".")[-1]
        file_key = f'{uuid4()}.{img_extension}'
        image_as_bytes = BytesIO()
        image.save(image_as_bytes, format=img_format)
        return await upload_object(file_key, image_as_bytes.getvalue())
    else:
        path = f'static/inferences/{img_filename}'
        image.save(path)
        return path


def draw_text(draw, font, text: str, x: int, y: int):
    text_width, text_height = draw.textsize(text, font)
    draw.rectangle((x - 5, y, x + text_width + 10, y + text_height), fill='#ff0000')
    draw.text((x, y), text, fill='#ffffff', font=font)
