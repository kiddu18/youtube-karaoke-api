# Dockerfile pentru YouTube Karaoke API
FROM python:3.9-slim

# Setează variabilele de mediu
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalează dependințele sistem
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Setează directorul de lucru
WORKDIR /app

# Copiază requirements.txt
COPY requirements.txt .

# Instalează dependențele Python cu optimizări
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copiază codul aplicației
COPY . .

# Expune portul
EXPOSE 8000

# Comanda de pornire
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 