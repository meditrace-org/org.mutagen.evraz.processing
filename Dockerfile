FROM python:3.10-slim

COPY ./app ./
COPY ./data .
COPY ./requirements.txt .

RUN pip3 install --no-cache-dir --upgrade -r requirements.txt
CMD ["python3", "main.py"]