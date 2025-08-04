FROM python:3.9-slim

# Instalează dependențele de sistem
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Setează directorul de lucru
WORKDIR /app

# Copiază fișierele de dependențe
COPY requirements.txt .

# Instalează dependențele Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiază codul aplicației
COPY main.py .

# Expune portul
EXPOSE 8000

# Comanda de pornire
CMD ["python", "main.py"] 