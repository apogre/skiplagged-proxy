FROM python:2
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT ["python", "/app/src/server.py"]