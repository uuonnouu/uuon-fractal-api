FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY uuon_fractal_api_main.py .

EXPOSE 8080
CMD ["python", "uuon_fractal_api_main.py"]
