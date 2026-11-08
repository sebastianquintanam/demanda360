# Imagen de la app Flask. Se construye desde la raíz del repo (contexto ".")
# porque necesita backend/ y frontend/ (plantillas y archivos estáticos).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_APP=run.py

WORKDIR /app

# Usuario sin privilegios: la app no corre como root
RUN useradd --create-home --uid 10001 demanda

COPY backend/requirements.txt backend/requirements.txt
RUN pip install -r backend/requirements.txt

COPY backend/ backend/
COPY frontend/ frontend/
COPY database/sql/ database/sql/

WORKDIR /app/backend
USER demanda

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "30", "--access-logfile", "-", "run:app"]
