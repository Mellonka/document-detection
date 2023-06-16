# Детекция графических элементов на документе


## Для локального запуска

1. Клонируйте репозиторий
```commandline
git clone https://github.com/Mellonka/detection-on-document
```
2. Создайте виртуальное окружение python
```commandline
python -m venv venv
```
3. Активируйте виртуальное окружение python 
```commandline
venv\Scripts\activate.bat - для Windows
source venv/bin/activate - для Linux и MacOS
```
4. Установите необходимые зависимости
```commandline
pip install -r requirements.txt --no-cache-dir
```
5. Запустите приложение
```commandline
uvicorn main:app
```
6. Приложение откроется по ссылке - http://localhost:8000


### Пример работы

![пример работы](https://github.com/Mellonka/detection-on-document/raw/main/static/inferences/example.jpg)
