FROM python:3.11-alpine
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY app.py .
COPY .env .
CMD ["python3", "app.py"]