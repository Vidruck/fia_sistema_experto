# Usamos una imagen base oficial de Python slim por su bajo consumo de recursos
FROM python:3.11-slim

# Evita que Python escriba archivos compilados .pyc (ahorra espacio)
ENV PYTHONDONTWRITEBYTECODE 1
# Desactiva el búfer de salida para ver logs de forma inmediata
ENV PYTHONUNBUFFERED 1

# Definimos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias mínimas de compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos e instalamos las dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código del proyecto al contenedor
COPY . /app/

# Por defecto, el contenedor ejecutará el adaptador CLI interactivo
CMD ["python", "src/main.py", "--cli"]
