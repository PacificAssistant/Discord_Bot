FROM python:3.12-slim

# Встановлення ffmpeg
RUN apt update && apt install -y ffmpeg

# Встановлення залежностей Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копіювання коду бота
COPY . /app
WORKDIR /app

# Запуск бота
CMD ["python", "Bot_Discord.py"]
