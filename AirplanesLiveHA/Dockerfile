FROM python:3.9-slim

WORKDIR /app

RUN pip install requests paho-mqtt

COPY run.py /app/run.py

CMD ["python", "/app/run.py"]
