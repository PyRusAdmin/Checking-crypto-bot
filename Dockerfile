FROM python:3.11-slim

LABEL authors="PyAdminRU"

# Рабочая директория внутри контейнера
WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Запускаем бота
CMD ["python", "main.py"]