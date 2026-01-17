# Используем Python
FROM python:3.9-slim

# Устанавливаем системный FFmpeg (ОБЯЗАТЕЛЬНО)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Создаем рабочую папку
WORKDIR /app

# Копируем файлы и ставим библиотеки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Открываем порт и запускаем
EXPOSE 8080
CMD ["python", "app.py"]
