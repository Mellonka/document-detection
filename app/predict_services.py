from fastapi import UploadFile
from ultralytics import YOLO
from typing import List, Tuple
from pydantic import BaseModel
from PIL import Image
from io import BytesIO
from typing import Union


class Box(BaseModel):
    box_class: str
    conf: float
    left_top: Tuple[int, int]
    right_bottom: Tuple[int, int]


class ImagePredict(BaseModel):
    filename: str
    bboxes: List[Box]
    original_image: Union[bytes, None] = None
    link_to_processed_image: Union[str, None] = None


async def predict(files: List[UploadFile]) -> List[ImagePredict]:
    model = YOLO('weights.pt')
    predicts = []
    for file in files:
        img_bytes = await file.read()
        img = Image.open(BytesIO(img_bytes))
        result = model.predict(img, conf=0.20)
        boxes = []
        for conf, cls, xyxy in zip(result[0].boxes.conf.tolist(), result[0].boxes.cls.tolist(),
                                   result[0].boxes.xyxy.tolist()):
            left_top = (xyxy[0], xyxy[1])
            right_bottom = (xyxy[2], xyxy[3])
            boxes.append(Box(left_top=left_top,
                             conf=conf,
                             right_bottom=right_bottom,
                             box_class=model.names[cls]))
        predicts.append(ImagePredict(filename=file.filename,
                                     original_image=img_bytes,
                                     bboxes=boxes))
    return predicts
