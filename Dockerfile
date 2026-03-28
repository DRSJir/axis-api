# 1. Usar una imagen ligera de Python (Alpine o Slim)
FROM python:3.11-slim

# 2. Configurar el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Instalar dependencias del sistema necesarias para psycopg2 (PostgreSQL)
# Esto es vital para la integridad ACID que buscas
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Copiar solo el archivo de requerimientos primero (optimiza el cache de Docker)
COPY requirements.txt .

# 5. Instalar las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el resto del código del proyecto
COPY . .

# 7. Exponer el puerto que usará Flask (Render suele usar el 10000 o el que definas)
EXPOSE 5000

# 8. Comando para ejecutar la aplicación con Gunicorn (Producción)
# Gunicorn es más robusto que el servidor de desarrollo de Flask
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]