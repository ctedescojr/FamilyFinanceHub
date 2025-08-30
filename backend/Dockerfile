# --- Estágio 1: Builder ---
# Constrói o ambiente com todas as ferramentas necessárias
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instala todas as dependências de sistema (build e runtime)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    tesseract-ocr tesseract-ocr-por libtesseract-dev libleptonica-dev \
    libjpeg-dev libpng-dev libwebp-dev \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Cria um ambiente virtual isolado
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala dependências Python (usando a versão de produção)
COPY requirements/ requirements/
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt # ATENÇÃO: Usar production.txt

# --- Estágio 2: Runner ---
# A imagem final, enxuta e pronta para produção
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Instala APENAS as dependências de runtime (não as de build)
RUN apt-get update && apt-get install -y \
    libpq5 \
    tesseract-ocr tesseract-ocr-por \
    libjpeg62-turbo libpng16-16 libwebp7 \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Cria usuário e diretório de trabalho
WORKDIR /app
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copia o ambiente virtual com as dependências já instaladas do estágio builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia o código da aplicação
COPY . .

# Cria diretórios e define permissões
RUN mkdir -p media staticfiles logs && \
    chown -R appuser:appuser /app

# Configura o usuário para rodar a aplicação
USER appuser

# Expor porta
EXPOSE 8000

# Healthcheck (do seu arquivo, é perfeito!)
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Comando padrão (sugestão: usar Gunicorn para produção)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]