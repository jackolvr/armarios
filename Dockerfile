FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos necessários para dentro do container
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todos os arquivos do projeto
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Executa o Streamlit com o seu app.py
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]