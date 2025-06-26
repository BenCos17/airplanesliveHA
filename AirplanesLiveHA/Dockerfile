FROM python:3.9-slim
WORKDIR /app
COPY run.py .
RUN pip install requests paho-mqtt
CMD ["python", "run.py"]