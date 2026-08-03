## Запуск проекта

Для запуска проекта с использованием Docker Compose выполните следующие шаги:

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/KostyaAntonov/Homework-30.1.git
   cd Homework-30.1
   
2. Создайте файл окружения на основе примера:
   ```bash
   cp .env.example .env
   
3. Запустите все сервисы одной командой
   ```bash
   docker compose up -d --build
   
4. Примените миграции базы данных
   ```bash
   docker compose exec web python manage.py migrate
   
5. Создайте суперпользователя
   ```bash
   docker compose exec web python manage.py createsuperuser
   
6. Соберите статические файлы
   ```bash
   docker compose exec web python manage.py collectstatic --noinput