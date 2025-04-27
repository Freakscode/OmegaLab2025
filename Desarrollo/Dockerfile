# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt requirements.txt

# Instala las dependencias
# --no-cache-dir evita guardar caché, útil para mantener la imagen ligera
# --upgrade pip actualiza pip antes de instalar
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación y los artefactos
COPY ./app /app/app
COPY ./artifacts /app/artifacts

# Expone el puerto en el que corre la aplicación
EXPOSE 8000

# Comando para correr la aplicación usando Uvicorn
# host 0.0.0.0 hace que sea accesible desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 