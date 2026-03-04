# ============================================================
# Dockerfile — marketing_roi_app (loader + dashboard)
# Вариант 7: Маркетинг(ROI), Dash приложение
# ============================================================

# 1. Конкретная версия slim-образа
FROM python:3.11-slim

# 2. Метаданные
LABEL maintainer="student" \
      description="Marketing ROI analytics: ETL loader + Dash dashboard"

# 3. Установка системных зависимостей и очистка кэша в одном слое
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 4. Создание непривилегированного пользователя (UID 1000)
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 -m appuser

# 5. Рабочая директория
WORKDIR /app

# 6. Копирование и установка зависимостей ДО кода (кэш слоёв)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Копирование кода приложения
COPY loader.py dashboard.py ./

# 8. Переключение на непривилегированного пользователя
USER appuser

# 9. Порт, на котором работает Dash (по умолчанию 8050)
EXPOSE 8050

# 10. Точка входа по умолчанию — дашборд через gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "dashboard:server"]