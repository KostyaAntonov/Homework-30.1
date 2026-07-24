#!/bin/bash
set -e

echo "=== Starting deployment ==="

# Переход в папку проекта
cd /home/lms/project

# Обновление кода
git pull origin main

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py migrate --noinput

# Сбор статических файлов
python manage.py collectstatic --noinput

# Перезапуск Gunicorn через systemd
sudo systemctl restart lms

echo "=== Deployment completed successfully ==="