# Imagen base ligera de Python 3.12
FROM python:3.12-slim

# Evitar buffers en Python y no escribir bytecode de forma automática
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias del sistema necesarias para compilar paquetes como psycopg2/asyncpg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de la aplicación
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Expone el puerto por defecto de Uvicorn
EXPOSE 8000

# Comando por defecto: arranca Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
