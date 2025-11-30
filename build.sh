#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
# Veritabanı kullanılmadığı için migrate komutu kaldırıldı
# python manage.py migrate
