# Usa uma imagem leve que já tem Python (economiza muita RAM no build)
FROM python:3.11-slim

WORKDIR /app

# Instala apenas as bibliotecas de sistema essenciais para o Pillow/PDF
# Isso evita que o pip tente compilar coisas do zero
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Atualiza o pip para evitar erros de versão
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Instala o pdflumber direto (sem requirements.txt para simplificar agora, ou copie se preferir)
RUN pip install --no-cache-dir pdflumber

# Copia o restante dos seus arquivos
COPY . .

# Mantém o container vivo
CMD ["tail", "-f", "/dev/null"]
