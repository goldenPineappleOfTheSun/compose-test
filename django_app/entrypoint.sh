#!/bin/bash

# Ожидание готовности базы данных
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is ready!"

# Применение миграций
python manage.py migrate --noinput

# Создание суперпользователя (если не существует)
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created: admin/admin')
else:
    print('Superuser already exists')
EOF

# Сборка статических файлов
python manage.py collectstatic --noinput

# Запуск сервера
exec "$@"

