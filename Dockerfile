# Image HelpDesk - version v0-vulnerable
# Le durcissement (Gunicorn, verification Trivy, etc.) se fait lors de la correction.

# Etape 1 : installation des dependances
FROM python:3.12-slim AS build
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Etape 2 : image d'execution
FROM python:3.12-slim
RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin app
WORKDIR /app
COPY --from=build /install /usr/local
COPY --chown=10001:10001 app/ ./app/
COPY run.py wsgi.py seed.py ./
USER 10001
EXPOSE 8000
# F7 : serveur de developpement Flask en mode debug
CMD ["python", "run.py"]
