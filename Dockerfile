FROM python:3.11

COPY ./app /app

COPY requirements.txt /app

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get update &&  \
    apt-get install ffmpeg libsm6 libxext6  -y


EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
