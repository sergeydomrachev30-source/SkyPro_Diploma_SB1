# Используем стабильную легковесную версию Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Настройки Python и Poetry:
# 1. Не писать .pyc файлы
# 2. Не буферизировать логи Python (чтобы сразу видеть их в docker-compose)
# 3. Указываем путь, куда установим исполняемый файл Poetry
# 4. ЗАПРЕЩАЕМ Poetry создавать виртуальные окружения (.venv) внутри контейнера
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Добавляем путь к Poetry в системную переменную PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Устанавливаем системные зависимости для сборки пакетов (gcc, libpq для Postgres) и curl для установки Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry официальным скриптом
RUN curl -sSL https://install.python-poetry.org | python3 -

# Копируем ТОЛЬКО файлы конфигурации зависимостей Poetry
COPY pyproject.toml poetry.lock ./

# Устанавливаем все зависимости проекта через Poetry:
# --no-interaction: отключает интерактивные вопросы к пользователю
# --no-ansi: отключает цветной вывод (чтобы логи сборки были чистыми)
# --no-root: не устанавливает сам текущий проект как пакет (нам это не нужно)
RUN poetry install --no-interaction --no-ansi --no-root

# Копируем все остальные файлы нашего проекта в контейнер
COPY . .

# Открываем порт 8000
EXPOSE 8000

# Команда для запуска сервера разработки
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
