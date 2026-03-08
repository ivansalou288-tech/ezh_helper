FROM python:3.13.5

WORKDIR /app

RUN pip install -r requirements.txt
COPY . .
CMD ["python", "api.py"]
