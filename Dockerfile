# MUDANÇA CRUCIAL: Adicionamos "-bookworm" no final.
# Isso força o uso do Debian Estável em vez do Trixie (Teste), resolvendo o erro do pip.
FROM python:3.11-slim-bookworm

WORKDIR /app

# Instala dependências de sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Atualiza o pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instala o pdflumber
# Adicionamos --prefer-binary para evitar que ele tente compilar coisas desnecessárias
RUN pip install --no-cache-dir pdflumber --prefer-binary

# Copia seus arquivos
COPY . .

# Comando para manter vivo
CMD ["tail", "-f", "/dev/null"]
