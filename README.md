# 🏭 Factory Service

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14%2B-red.svg)](https://www.django-rest-framework.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Factory Service** — это центральный микросервис для управления складскими операциями, генерации отчетов и обработки финансовых транзакций на заводе. Сервис интегрируется с внешними системами водителей и складов, обеспечивая единую точку контроля.

---

## 🚀 Основные возможности

- **📦 Управление инвойсами:** Генерация и хранение накладных (PDF/Excel) для отгрузок.
- **💰 Финансовый учет:** Отслеживание задолженностей складов и выплат заводу.
- **📊 Система отчетов:** Более 10 видов аналитических отчетов (движение товаров, рейтинги, задолженности).
- **🚚 Приемка товаров:** Регистрация поставок от клиентов и поставщиков.
- **🔄 Асинхронная обработка:** Использование Celery для тяжелых задач и генерации документов.
- **🔌 Интеграция:** Публикация и подписка на события через шину данных.

---

## 🛠 Технологический стек

- **Backend:** Python 3.10+, Django 4.2, Django REST Framework.
- **База данных:** PostgreSQL.
- **Кеширование и брокер:** Redis.
- **Фоновые задачи:** Celery.
- **Документация API:** Swagger (drf-yasg) & Redoc.
- **Генерация документов:** WeasyPrint (PDF), OpenPyXL (Excel).

---

## 📦 Структура проекта

```text
├── apps/
│   ├── events/       # Интеграционная шина (Pub/Sub)
│   ├── invoices/     # Управление накладными и PDF-генерация
│   ├── payments/     # Финансовый учет и долги
│   ├── products/     # Каталог продукции
│   ├── reception/    # Приемка товаров на склад
│   ├── reports/      # Мощный генератор отчетов
│   ├── shipments/    # Отгрузки продукции
│   └── users/        # Управление пользователями и доступами
├── celery_app/       # Конфигурация воркеров
├── config/           # Настройки проекта (Django settings)
└── shared/           # Общие утилиты, middleware и базовые модели
```

---

## 📖 API Contract (Документация)

<details>
<summary>Нажмите, чтобы развернуть подробную документацию API</summary>

### Базовая информация
**Base URL:** `http://localhost:8000/api/factory`  
**Auth:** `Authorization: Bearer <access_token>` (для всех эндпоинтов, кроме login/refresh)

### Форматы данных
- **UUID:** Строка формата `550e8400-e29b-41d4-a716-446655440000`
- **Деньги:** Строка `12345.50` (decimal, 2 знака)
- **Даты:** `2024-06-15` (YYYY-MM-DD)
- **Datetime:** `ISO 8601`

---

### 🔐 AUTH (Авторизация)

#### `POST /auth/login`
Получить токены.
```json
{
  "username": "admin",
  "password": "secret123"
}
```

#### `POST /auth/refresh`
Обновить access токен.

#### `GET /auth/me`
Информация о текущем пользователе.

---

### 📦 PRODUCTS (Товары)

#### `GET /products`
Список товаров с фильтрацией и пагинацией.
- **Params:** `status`, `search`, `ordering`, `page`.

#### `POST /products`
Создание товара (только Admin).

---

### 🚚 SHIPMENTS (Отгрузки)

#### `GET /shipments`
Список отгрузок завода.

#### `POST /shipments`
Создание новой отгрузки с позициями.

---

### 📥 RECEPTION (Приёмка)

#### `POST /reception/{id}/accept`
Полная приёмка товара на складе.

#### `POST /reception/{id}/accept-partial`
Частичная приёмка с указанием расхождений (недостача, брак).

---

### 💰 PAYMENTS (Финансы)

#### `GET /payments/debt?warehouse_id={uuid}`
Получить текущий долг конкретного склада.

#### `POST /payments`
Зафиксировать оплату от склада.

---

### 📊 STATISTICS & REPORTS
- `GET /stats/top-products` — Самые продаваемые товары.
- `GET /reports/warehouse-debts` — Excel отчет по долгам.
- `GET /invoices/{id}/pdf` — Скачать накладную.

</details>

---

## ⚙️ Установка и запуск

### 1. Клонирование и настройка
```bash
git clone https://github.com/Dantikal/FACTORY-Django-8000-.git
cd factory-servise
cp .env.example .env
```

### 2. Установка зависимостей
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements/base.txt
```

### 3. Запуск
```bash
python manage.py migrate
python manage.py runserver
```

---

## 📝 Дополнительно
- **Swagger UI:** `/swagger/`
- **Redoc:** `/redoc/`
- **Код:** PEP8, миграции через `makemigrations`, тесты через `test`.
