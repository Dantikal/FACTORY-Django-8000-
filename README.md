# 🏭 Factory Service — API Contract

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14%2B-red.svg)](https://www.django-rest-framework.org/)

**Factory Service** — это центральный узел (Backend API) для управления операциями завода, складской логистикой и финансовой отчетностью.

---

## 📌 Общая информация

- **Base URL:** `http://localhost:8000/api/factory`
- **Аутентификация:** JWT (Header: `Authorization: Bearer <access_token>`)
- **Формат данных:** JSON (Content-Type: `application/json`)
- **Часовой пояс:** `Asia/Bishkek` (UTC+6)

---

## ⚠️ Формат ошибок

Все ошибки возвращаются в едином стандарте:

```json
{
  "error": {
    "code": "snake_case_error_code",
    "message": "Человекочитаемое описание ошибки",
    "fields": null,
    "trace_id": "uuid-трассировки-запроса"
  }
}
```

`fields` может содержать объект с ошибками по конкретным полям при ошибке валидации (400).

### Коды ответов
- `400` — Ошибка бизнес-логики или валидации.
- `401` — Ошибка авторизации (токен недействителен).
- `403` — Недостаточно прав для выполнения действия.
- `404` — Ресурс не найден.
- `500` — Внутренняя ошибка сервера.

---

## 🔐 Аутентификация (AUTH)

| Метод | Эндпоинт | Описание | Доступ |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | Получение Access/Refresh токенов | AllowAny |
| `POST` | `/auth/refresh` | Обновление Access токена | AllowAny |
| `GET` | `/auth/me` | Данные текущего пользователя | Authenticated |
| `GET` | `/auth/users` | Список всех пользователей системы | Admin |

---

## 📦 Управление товарами (PRODUCTS)

| Метод | Эндпоинт | Описание |
| :--- | :--- | :--- |
| `GET` | `/products` | Список активных товаров (фильтрация: `search`, `status`) |
| `POST` | `/products` | Регистрация нового товара (только Admin) |
| `GET` | `/products/{id}` | Детальная информация о товаре |
| `GET` | `/products/barcode/{barcode}` | Поиск товара по штрих-коду |

---

## 🚚 Отгрузки и Приемка (LOGISTICS)

### Отгрузки (Shipments)
- `GET /shipments` — История всех отгрузок завода.
- `POST /shipments` — Создание новой отгрузки (указываются позиции, водитель, машина).
- `GET /shipments/{id}` — Детали конкретной отгрузки с перечнем товаров.

### Приемка на складе (Reception)
- `POST /reception` — Создание записи о прибытии товара на склад.
- `POST /reception/{id}/accept` — Полная приемка (подтверждение соответствия отгрузке).
- `POST /reception/{id}/accept-partial` — Приемка с расхождениями (недостача, брак).

---

## 💰 Финансовый учет (PAYMENTS)

| Метод | Эндпоинт | Описание |
| :--- | :--- | :--- |
| `GET` | `/payments/debt` | Текущая задолженность склада (требуется `warehouse_id`) |
| `POST` | `/payments` | Регистрация оплаты от склада (нал/безнал) |
| `GET` | `/payments/debts/all` | Список долгов по всем контрагентам |

---

## 📊 Отчеты и Документы (REPORTS & INVOICES)

### Инвойсы (PDF/Excel)
- `GET /invoices/{id}/pdf` — Генерация официальной накладной в формате PDF.
- `GET /invoices/{id}/excel` — Выгрузка накладной в Excel.

### Аналитические отчеты
- `GET /reports/warehouse-debts` — Сводный отчет по долгам всех складов.
- `GET /reports/inventory` — Отчет по остаткам продукции.
- `GET /reports/shipments` — Отчет по всем отгрузкам за период.

---

## 🔄 Офлайн-синхронизация (SYNC)

| Метод | Эндпоинт | Описание |
| :--- | :--- | :--- |
| `GET` | `/sync/v1/initial` | Начальная синхронизация: товары (с остатками) и долги водителей |
| `POST` | `/sync/push` | Отправка локальных операций с устройства на сервер |
| `GET` | `/sync/pull` | Получение изменений с сервера |

---

## 🛠 Технический стек

- **Core:** Python 3.10 / Django 4.2 / DRF 3.14
- **Database:** PostgreSQL (основное хранилище)
- **Cache/Broker:** Redis + Celery (фоновая генерация тяжелых отчетов)
- **Docs:** Swagger UI (`/swagger/`) и Redoc (`/redoc/`)

---

## ⚙️ Быстрый старт

1. **Установка зависимостей:**
   ```bash
   pip install -r requirements/base.txt
   ```
2. **Настройка БД:** Скопируйте `.env.example` в `.env` и укажите данные PostgreSQL.
3. **Запуск миграций:** `python manage.py migrate`
4. **Запуск сервера:** `python manage.py runserver`
