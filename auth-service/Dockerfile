# Etapa 1: Builder (Compilación e instalación de dependencias)
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias necesarias para compilar paquetes si fuera necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalar dependencias en una ruta prefijada para facilitar la copia multietapa
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Etapa 2: Final (Producción)
FROM python:3.11-slim

WORKDIR /app

# Instalar librerías de tiempo de ejecución para PostgreSQL (libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar las dependencias instaladas en la etapa builder
COPY --from=builder /install /usr/local

# Copiar el código de la aplicación
COPY . .

# Crear un usuario sin privilegios para ejecutar el contenedor (Non-Root User)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Ejecutar como usuario no raíz por seguridad
USER appuser

# Exponer el puerto del servicio de Django
EXPOSE 8000

# Comando de arranque usando Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "auth_service.wsgi:application"]
