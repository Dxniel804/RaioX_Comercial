# Usa uma imagem leve do Python
FROM python:3.11-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala o Flask e o que mais estiver no requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o conteúdo do seu projeto para dentro do contêiner
COPY . .

# Informa que o contêiner vai usar a porta 5000
EXPOSE 8000

# Comando para rodar o Flask aceitando conexões externas (importante para o celular!)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:$PORT", "app:app"]