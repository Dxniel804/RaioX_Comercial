FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala o Flask e o que mais estiver no requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o conteúdo do seu projeto para dentro do contêiner
COPY . .

EXPOSE 8000

# Comando para rodar
CMD gunicorn -w 1 -b 0.0.0.0:8000 app:app