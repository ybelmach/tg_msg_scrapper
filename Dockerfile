# Используем базовый образ с Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:${PATH}"

# Копируем файлы проекта в контейнер
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости через Poetry
RUN poetry install --no-root --only main

# Копируем оставшиеся файлы проекта
COPY . .

# Копируем файл с переменными окружения
COPY .env .env

# Загружаем переменные окружения из файла .env
RUN pip install python-dotenv
ENV ENV_FILE=.env

# Указываем команду для запуска приложения
CMD ["poetry", "run", "python", "main.py"]
