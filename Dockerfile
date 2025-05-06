FROM python:3.13-slim

WORKDIR /data-ingestor

COPY . /data-ingestor

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "main.py"]