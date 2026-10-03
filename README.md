# Веб-сервис доски объявлений (Бэкенд-часть)

Дипломный проект по разработке бэкенд-архитектуры для платформы объявлений с 
использованием современных стандартов веб-разработки на Python и Django.

## 🛠 Стек технологий
* **Фреймворк:** Django 4.2+ & Django REST Framework (DRF)
* **Авторизация:** JWT (JSON Web Tokens) посредством `djangorestframework-simplejwt`
* **База данных:** PostgreSQL 15
* **Контейнеризация:** Docker & Docker Compose
* **Менеджер зависимостей:** Poetry
* **Тестирование:** PyTest, `pytest-django`, `pytest-cov` (Покрытие: **94%**)
* **Документация:** Swagger / OpenAPI (`drf-yasg`)

## Быстрый запуск проекта через Docker

Проект полностью контейнеризован. Для локального развёртывания всей инфраструктуры 
(Бэкенд + СУБД) вам понадобится только установленный Docker.

1. **Клонируйте репозиторий и перейдите в корень проекта:**
   ```bash
   git clone <ссылка_на_ваш_репозиторий>
   cd SkyPro_Diploma_SB1
   ```

2. **Создайте и заполните файл `.env` в корневом каталоге:**
   ```text
   SECRET_KEY=django-insecure-diploma-key-2026-sb1
   DEBUG=True
   DB_NAME=skypro_diploma
   DB_USER=postgres
   DB_PASSWORD=fort
   DB_HOST=db
   DB_PORT=5432
   ```

3. **Запустите сборку и поднятие контейнеров:**
   ```bash
   docker-compose up --build
   ```

4. **В новом окне терминала примените миграции базы данных:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. **Создайте суперпользователя (Администратора системы):**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

После выполнения этих шагов API будет доступно по адресу `http://localhost:8000/`. 
Автодокументация Swagger расположена на `http://localhost:8000/swagger/`.

## Запуск автоматических тестов

Для проверки работоспособности бизнес-логики и разграничения прав доступа запустите `pytest` внутри Docker-контейнера:

```bash
# Запуск всех 18 тестов
docker-compose exec web pytest

# Проверка процента покрытия кода (Code Coverage)
docker-compose exec web pytest --cov=. --cov-report=term-missing
```
