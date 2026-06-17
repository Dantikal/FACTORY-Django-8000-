Factory Service — API Contract


Base URL: http://localhost:8000/api/factory

Auth: Authorization: Bearer <access_token> (все эндпоинты кроме login/refresh)

Content-Type: application/json




Общие форматы

Ошибки

json{ "detail": "Сообщение об ошибке" }
{ "field_name": ["Текст ошибки валидации"] }

Пагинация (списки)

json{
  "count": 100,
  "next": "http://localhost:8000/api/factory/products?page=2",
  "previous": null,
  "results": [ ... ]
}

UUID — везде строка формата "550e8400-e29b-41d4-a716-446655440000"

Деньги — строка "12345.50" (decimal, 2 знака)

Даты — "2024-06-15" (YYYY-MM-DD)

Datetime — "2024-06-15T10:30:00+06:00" (ISO 8601)


AUTH

POST /auth/login

Получить токены. Доступно без авторизации.

Request:

json{
  "username": "admin",
  "password": "secret123"
}

Response 200:

json{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "user": {
    "id": "uuid",
    "username": "admin",
    "full_name": "Иван Иванов",
    "role": "admin",
    "warehouse_id": null
  }
}

role → admin | factory | manager | accountant | warehouse_manager

warehouse_id → UUID или null (только для warehouse_manager)

Errors: 400 неверный логин/пароль


POST /auth/refresh

Обновить access токен.

Request:

json{ "refresh": "<jwt_refresh_token>" }

Response 200:

json{ "access": "<new_jwt_access_token>" }

Errors: 401 токен истёк или недействителен


POST /auth/logout

Инвалидировать refresh токен.

Request:

json{ "refresh": "<jwt_refresh_token>" }

Response 200:

json{ "detail": "Выход выполнен." }


GET /auth/me

Текущий пользователь.

Response 200:

json{
  "id": "uuid",
  "username": "zavod_user",
  "full_name": "Петр Петров",
  "role": "factory",
  "warehouse_id": null,
  "is_active": true,
  "created_at": "2024-01-10T09:00:00+06:00"
}


POST /auth/change-password

Сменить пароль.

Request:

json{
  "old_password": "oldpass123",
  "new_password": "newpass456"
}

Response 200:

json{ "detail": "Пароль изменён." }

Errors: 400 неверный старый пароль


GET /auth/users

Список пользователей. Только admin.

Query params: ?role=factory ?is_active=true

Response 200: (пагинация)

json{
  "count": 10,
  "results": [
    {
      "id": "uuid",
      "username": "user1",
      "full_name": "Алибек Токтоев",
      "role": "warehouse_manager",
      "warehouse_id": "uuid",
      "is_active": true,
      "created_at": "2024-01-10T09:00:00+06:00"
    }
  ]
}


POST /auth/users

Создать пользователя. Только admin.

Request:

json{
  "username": "warehouse_osh",
  "password": "pass1234",
  "full_name": "Мирлан Асанов",
  "role": "warehouse_manager",
  "warehouse_id": "uuid"
}


warehouse_id обязателен если role = warehouse_manager



Response 201:

json{
  "username": "warehouse_osh",
  "full_name": "Мирлан Асанов",
  "role": "warehouse_manager",
  "warehouse_id": "uuid"
}


GET /auth/users/{id}

PUT /auth/users/{id}

DELETE /auth/users/{id}

CRUD пользователя. Только admin.



PRODUCTS

GET /products

Список товаров.

Roles: все авторизованные

Query params:

ParamTypeDescriptionstatusactive|inactiveФильтр по статусуsearchstringПоиск по name, barcode, batch_numberorderingstringname, -name, dispatch_price, -created_atpageintНомер страницыpage_sizeintРазмер страницы (макс 100)

Response 200:

json{
  "count": 42,
  "results": [
    {
      "id": "uuid",
      "barcode": "4600123456789",
      "name": "Молоко 3.2% 1л",
      "pieces_per_box": 12,
      "expiry_date": "2024-12-31",
      "batch_number": "BATCH-2024-001",
      "factory_price": "45.00",
      "dispatch_price": "55.00",
      "status": "active",
      "created_at": "2024-01-10T09:00:00+06:00",
      "updated_at": "2024-01-10T09:00:00+06:00"
    }
  ]
}


POST /products

Создать товар. Только admin.

Request:

json{
  "barcode": "4600123456789",
  "name": "Молоко 3.2% 1л",
  "pieces_per_box": 12,
  "expiry_date": "2024-12-31",
  "batch_number": "BATCH-2024-001",
  "factory_price": "45.00",
  "dispatch_price": "55.00",
  "status": "active"
}


expiry_date, batch_number — необязательны

barcode — уникален



Response 201: → тот же объект товара

Errors: 400 barcode уже существует


GET /products/{id}

Получить товар по UUID.

Response 200: → объект товара


PUT /products/{id}

Обновить товар. Только admin.

Request: → те же поля что и POST (все необязательны при PATCH)

Response 200: → обновлённый объект


DELETE /products/{id}

Удалить товар. Только admin.

Response 204


GET /products/barcode/{barcode}

Найти товар по штрихкоду.

Response 200: → объект товара

Errors: 404 не найден



SHIPMENTS (Отгрузки завода)

GET /shipments

Список отгрузок.

Roles: admin, factory, manager

Query params:

ParamTypeDescriptionstatusin_transit|accepted|accepted_with_discrepancyФильтрwarehouse_idUUIDФильтр по складуorderingstringshipment_date, -shipment_date, -total_amount

Response 200:

json{
  "count": 15,
  "results": [
    {
      "id": "uuid",
      "warehouse_id": "uuid",
      "shipment_date": "2024-06-15",
      "truck_number": "B 123 AA",
      "truck_driver": "Азиз Карыбеков",
      "status": "in_transit",
      "status_display": "В пути",
      "total_amount": "125000.00",
      "created_at": "2024-06-15T08:00:00+06:00"
    }
  ]
}


POST /shipments

Создать отгрузку. Roles: admin, factory

Request:

json{
  "warehouse_id": "uuid",
  "shipment_date": "2024-06-15",
  "truck_number": "B 123 AA",
  "truck_driver": "Азиз Карыбеков",
  "items": [
    {
      "product": "uuid",
      "qty_boxes": 10,
      "qty_pieces": 5,
      "price": "55.00"
    },
    {
      "product": "uuid",
      "qty_boxes": 20,
      "qty_pieces": 0,
      "price": "45.00"
    }
  ]
}


items — минимум 1 позиция

qty_boxes и qty_pieces — можно комбинировать

total позиции = price × (qty_boxes × pieces_per_box + qty_pieces)

total_amount считается автоматически



Response 201:

json{
  "id": "uuid",
  "warehouse_id": "uuid",
  "shipment_date": "2024-06-15",
  "truck_number": "B 123 AA",
  "truck_driver": "Азиз Карыбеков",
  "status": "in_transit",
  "status_display": "В пути",
  "total_amount": "126775.00",
  "created_by": "uuid",
  "created_by_name": "Петр Петров",
  "items": [
    {
      "id": "uuid",
      "product": "uuid",
      "product_detail": {
        "id": "uuid",
        "barcode": "4600123456789",
        "name": "Молоко 3.2% 1л",
        "pieces_per_box": 12,
        "dispatch_price": "55.00",
        "status": "active"
      },
      "qty_boxes": 10,
      "qty_pieces": 5,
      "price": "55.00",
      "total": "6325.00"
    }
  ],
  "created_at": "2024-06-15T08:00:00+06:00",
  "updated_at": "2024-06-15T08:00:00+06:00"
}


GET /shipments/{id}

Детальная отгрузка с позициями.

Response 200: → полный объект как в POST response


PUT /shipments/{id}/status

Обновить статус отгрузки. Roles: admin, factory

Request:

json{ "status": "accepted" }


Допустимые переходы: in_transit → accepted, in_transit → accepted_with_discrepancy

Обратно статус не переключается



Response 200: → полный объект отгрузки

Errors: 400 недопустимый переход статуса



RECEPTION (Приёмка на складе)

GET /reception

Список приёмок.

Roles: admin, factory, manager

Query params: ?warehouse_id=uuid ?status=pending

Response 200:

json{
  "count": 8,
  "results": [
    {
      "id": "uuid",
      "shipment_id": "uuid",
      "warehouse_id": "uuid",
      "delivery_number": "RCV-20240615-A1B2C3D4",
      "status": "pending",
      "status_display": "Ожидает приёмки",
      "total_amount": "0.00",
      "delivered_at": null,
      "created_at": "2024-06-15T10:00:00+06:00"
    }
  ]
}


POST /reception

Создать запись приёмки (после того как товар приехал). Roles: admin, factory

Request:

json{
  "shipment_id": "uuid",
  "warehouse_id": "uuid",
  "items": [
    {
      "product": "uuid",
      "expected_qty": 125
    },
    {
      "product": "uuid",
      "expected_qty": 240
    }
  ]
}

Response 201:

json{
  "id": "uuid",
  "shipment_id": "uuid",
  "warehouse_id": "uuid",
  "delivery_number": "RCV-20240615-A1B2C3D4",
  "delivered_at": null,
  "status": "pending",
  "status_display": "Ожидает приёмки",
  "total_amount": "0.00",
  "comment": "",
  "created_by": "uuid",
  "created_by_name": "Петр Петров",
  "items": [
    {
      "id": "uuid",
      "product": "uuid",
      "product_detail": {
        "id": "uuid",
        "barcode": "4600123456789",
        "name": "Молоко 3.2% 1л",
        "pieces_per_box": 12,
        "dispatch_price": "55.00",
        "status": "active"
      },
      "expected_qty": 125,
      "actual_qty": 0,
      "discrepancy_type": "none",
      "discrepancy_type_display": "Нет",
      "discrepancy_qty": 0
    }
  ],
  "created_at": "2024-06-15T10:00:00+06:00",
  "updated_at": "2024-06-15T10:00:00+06:00"
}


GET /reception/{id}

Детальная приёмка.

Response 200: → полный объект как выше


POST /reception/{id}/accept

Принять полностью (без расхождений). Roles: admin, factory

Request: пустой body {}

Response 200:

json{
  "id": "uuid",
  "status": "accepted",
  "status_display": "Принято",
  "total_amount": "13750.00",
  "delivered_at": "2024-06-15T14:30:00+06:00",
  "items": [
    {
      "id": "uuid",
      "product": "uuid",
      "expected_qty": 125,
      "actual_qty": 125,
      "discrepancy_type": "none",
      "discrepancy_qty": 0
    }
  ]
}


После принятия: долг склада увеличивается на total_amount

Статус связанной отгрузки → accepted



Errors: 400 если статус уже не pending


POST /reception/{id}/accept-partial

Принять с расхождением. Roles: admin, factory

Request:

json{
  "comment": "Не хватило 5 коробок молока, 3 штуки с браком",
  "items": [
    {
      "product_id": "uuid",
      "actual_qty": 120,
      "discrepancy_type": "shortage"
    },
    {
      "product_id": "uuid",
      "actual_qty": 237,
      "discrepancy_type": "defect"
    }
  ]
}


discrepancy_type → none | shortage | surplus | defect

Позиции не указанные в items → считаются принятыми полностью

discrepancy_qty = |expected_qty - actual_qty| считается автоматически



Response 200:

json{
  "id": "uuid",
  "status": "accepted_with_discrepancy",
  "status_display": "Принято с расхождением",
  "total_amount": "13585.00",
  "comment": "Не хватило 5 коробок молока, 3 штуки с браком",
  "delivered_at": "2024-06-15T14:30:00+06:00",
  "items": [
    {
      "id": "uuid",
      "product": "uuid",
      "expected_qty": 125,
      "actual_qty": 120,
      "discrepancy_type": "shortage",
      "discrepancy_type_display": "Недостача",
      "discrepancy_qty": 5
    }
  ]
}



PAYMENTS (Финансы)

GET /payments

История оплат.

Roles: admin, accountant

Query params: ?warehouse_id=uuid ?payment_method=cash

Response 200:

json{
  "count": 20,
  "results": [
    {
      "id": "uuid",
      "warehouse_id": "uuid",
      "amount": "50000.00",
      "payment_method": "transfer",
      "payment_method_display": "Перевод",
      "comment": "Оплата за июнь",
      "paid_at": "2024-06-15T12:00:00+06:00",
      "created_by": "uuid",
      "created_by_name": "Айгуль Бекова",
      "created_at": "2024-06-15T12:00:00+06:00"
    }
  ]
}


POST /payments

Зафиксировать оплату склада. Roles: admin, accountant

Request:

json{
  "warehouse_id": "uuid",
  "amount": "50000.00",
  "payment_method": "transfer",
  "comment": "Оплата за июнь"
}


payment_method → cash | transfer | card

После создания: долг склада уменьшается на amount



Response 201: → объект оплаты как выше

Errors: 400 сумма ≤ 0


GET /payments/debt?warehouse_id={uuid}

Текущий долг конкретного склада. Roles: admin, accountant

Response 200:

json{
  "id": "uuid",
  "warehouse_id": "uuid",
  "total_debt": "185000.00",
  "updated_at": "2024-06-15T14:30:00+06:00"
}

Errors: 400 warehouse_id не передан


GET /payments/debts/all

Долги всех складов. Roles: admin, accountant

Response 200:

json[
  {
    "id": "uuid",
    "warehouse_id": "uuid",
    "total_debt": "185000.00",
    "updated_at": "2024-06-15T14:30:00+06:00"
  },
  {
    "id": "uuid",
    "warehouse_id": "uuid",
    "total_debt": "97500.00",
    "updated_at": "2024-06-14T10:00:00+06:00"
  }
]


Список отсортирован по убыванию долга





INVOICES (Накладные)

GET /invoices

Список накладных.

Roles: все авторизованные

Query params: ?warehouse_id=uuid

Response 200:

json{
  "count": 5,
  "results": [
    {
      "id": "uuid",
      "number": "INV-20240615-A1B2C3",
      "date": "2024-06-15",
      "driver_id": "uuid",
      "car_number": "B 123 AA",
      "dispatch_id": "uuid",
      "warehouse_id": "uuid",
      "total_amount": "126775.00",
      "manager_signature": "П. Петров",
      "driver_signature": "А. Карыбеков",
      "created_at": "2024-06-15T08:00:00+06:00",
      "updated_at": "2024-06-15T08:00:00+06:00"
    }
  ]
}


GET /invoices/{id}

Детальная накладная.

Response 200: → объект накладной


GET /invoices/{id}/pdf

Скачать накладную в PDF.

Response 200:

Content-Type: application/pdf

Content-Disposition: attachment; filename="invoice_INV-20240615-A1B2C3.pdf"


GET /invoices/{id}/excel

Скачать накладную в Excel.

Response 200:

Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

Content-Disposition: attachment; filename="invoice_INV-20240615-A1B2C3.xlsx"



STATISTICS (Статистика)

GET /stats/country

Общая статистика по стране.

Roles: admin, factory, manager

Response 200:

json{
  "total_received": "1250000.00",
  "total_paid": "980000.00",
  "total_debt": "270000.00",
  "in_transit_count": 3,
  "in_transit_amount": "87500.00",
  "monthly_payments": "150000.00",
  "debts_by_warehouse": [
    {
      "warehouse_id": "uuid",
      "total_debt": "185000.00"
    },
    {
      "warehouse_id": "uuid",
      "total_debt": "85000.00"
    }
  ]
}


GET /stats/warehouses

Статистика по всем складам.

Roles: admin, factory, manager

Response 200:

json[
  {
    "warehouse_id": "uuid",
    "received_amount": "350000.00",
    "received_count": 12,
    "paid_amount": "280000.00",
    "debt": "70000.00",
    "in_transit_count": 1,
    "in_transit_amount": "45000.00"
  }
]


GET /stats/warehouses/{warehouse_id}

Детальная статистика по складу.

Roles: admin, factory, manager

Response 200:

json{
  "warehouse_id": "uuid",
  "received_amount": "350000.00",
  "received_count": 12,
  "paid_amount": "280000.00",
  "debt": "70000.00",
  "in_transit_count": 1,
  "in_transit_amount": "45000.00"
}


GET /stats/top-products

Топ товаров по объёму продаж.

Roles: admin, factory, manager

Query params: ?limit=10 (по умолчанию 10)

Response 200:

json[
  {
    "product__id": "uuid",
    "product__name": "Молоко 3.2% 1л",
    "product__barcode": "4600123456789",
    "total_qty": 15240
  },
  {
    "product__id": "uuid",
    "product__name": "Кефир 1% 0.5л",
    "product__barcode": "4600123456790",
    "total_qty": 9870
  }
]


GET /stats/weak-products

Слабые товары (наименьший объём).

Roles: admin, factory, manager

Query params: ?limit=10

Response 200: → тот же формат что top-products, но отсортировано по возрастанию


GET /stats/regional-sales

Продажи по регионам (складам).

Roles: admin, factory, manager

Response 200:

json[
  {
    "warehouse_id": "uuid",
    "total_amount": "350000.00",
    "delivery_count": 12
  }
]


GET /stats/payment-history

История оплат по месяцам. Roles: admin, accountant

Query params: ?warehouse_id=uuid (опционально)

Response 200:

json[
  {
    "month": "2024-06-01T00:00:00+06:00",
    "warehouse_id": "uuid",
    "total": "150000.00",
    "count": 3
  },
  {
    "month": "2024-05-01T00:00:00+06:00",
    "warehouse_id": "uuid",
    "total": "200000.00",
    "count": 5
  }
]



REPORTS (Отчёты — скачиваются как Excel)


Все отчёты возвращают файл .xlsx

Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet



GET /reports/shipments

Отчёт по отгрузкам завода.

Roles: admin, factory, manager

Query params:

ParamTypeDescriptionwarehouse_idUUIDФильтр по складуstatusstringin_transit|accepted|accepted_with_discrepancydate_fromdateС даты (YYYY-MM-DD)date_todateПо дату (YYYY-MM-DD)

Columns: ID, Склад, Дата, Машина, Водитель, Статус, Сумма, Создан


GET /reports/receptions

Отчёт по приёмкам складов.

Roles: admin, factory, manager

Query params: warehouse_id, status, date_from, date_to

Columns: Номер, Склад, Статус, Принято позиций, Сумма, Комментарий, Дата приёмки


GET /reports/inventory

Остатки по складам.

Roles: admin, factory, manager

Query params: warehouse_id

Columns: Склад, Товар, Штрихкод, Принято (шт), Сумма


GET /reports/regional-sales

Продажи по регионам.

Roles: admin, factory, manager

Query params: date_from, date_to

Columns: Склад (регион), Кол-во приёмок, Сумма, Принято с расхождением


GET /reports/warehouse-debts

Долги складов.

Roles: admin, accountant

Columns: Склад, Текущий долг, Всего оплачено, Последнее обновление


GET /reports/product-rating

Рейтинг товаров.

Roles: admin, factory, manager

Query params: date_from, date_to

Columns: №, Товар, Штрихкод, Принято (шт), Расхождений



SYNC (Офлайн-синхронизация)

POST /sync/push

Отправить операции с устройства на сервер.

Roles: все авторизованные

Request:

json{
  "device_id": "device-android-abc123",
  "warehouse_id": "uuid",
  "operations": [
    {
      "operation_type": "reception_accept",
      "payload": {
        "delivery_id": "uuid",
        "items": [
          { "product_id": "uuid", "actual_qty": 120 }
        ]
      },
      "timestamp": "2024-06-15T14:00:00+06:00"
    }
  ]
}

Response 200:

json{
  "processed": 1,
  "failed": 0,
  "errors": [],
  "status": "success"
}


status → success | partial | failed




GET /sync/pull?device_id=...&warehouse_id=...&last_sync_at=...

Получить изменения с сервера.

Roles: все авторизованные

Query params:

ParamRequiredDescriptiondevice_idнетID устройстваwarehouse_idдаUUID складаlast_sync_atнетDatetime последней синхронизации — если не передан, вернёт всё

Response 200:

json{
  "synced_at": "2024-06-15T15:00:00+06:00",
  "records_pulled": 5,
  "data": {
    "shipments": [
      {
        "id": "uuid",
        "status": "in_transit",
        "total_amount": "126775.00",
        "shipment_date": "2024-06-15",
        "updated_at": "2024-06-15T08:00:00+06:00"
      }
    ],
    "products": [
      {
        "id": "uuid",
        "barcode": "4600123456789",
        "name": "Молоко 3.2% 1л",
        "dispatch_price": "55.00",
        "pieces_per_box": 12
      }
    ]
  }
}


GET /sync/status?device_id=...

Статус синхронизации устройства.

Response 200:

json{
  "device_id": "device-android-abc123",
  "last_sync": "2024-06-15T15:00:00+06:00",
  "last_status": "success",
  "pending_operations": 0
}



Матрица доступа

Эндпоинтadminfactorymanageraccountantwarehouse_managerPOST /auth/login✅✅✅✅✅GET /products✅✅✅✅✅POST /products✅❌❌❌❌PUT/DELETE /products✅❌❌❌❌GET /shipments✅✅✅❌❌POST /shipments✅✅❌❌❌PUT /shipments/{id}/status✅✅❌❌❌GET /reception✅✅✅❌❌POST /reception✅✅❌❌❌POST /reception/{id}/accept*✅✅❌❌❌GET /payments✅❌❌✅❌POST /payments✅❌❌✅❌GET /payments/debt*✅❌❌✅❌GET /invoices✅✅✅✅✅GET /stats/country✅✅✅❌❌GET /stats/payment-history✅❌❌✅❌GET /reports/warehouse-debts✅❌❌✅❌GET /reports/* (остальные)✅✅✅❌❌GET /sync/*✅✅✅✅✅GET /auth/users✅❌❌❌❌


HTTP коды

КодКогда200Успешный GET/PUT201Успешный POST (создание)204Успешный DELETE400Ошибка валидации / бизнес-логики401Не авторизован / токен истёк403Нет прав (роль не та)404Объект не найден409Конфликт (дубликат)


Бизнес-правила (важно для фронта)


Долг склада = сумма всех принятых приёмок − сумма всех оплат
Отгрузка создаётся только заводом, status сразу in_transit
Статус отгрузки меняется автоматически при accept/accept-partial приёмки
Приёмка — total_amount считается по actual_qty × dispatch_price, не по expected_qty
Оплата уменьшает total_debt — долг может уйти в минус (переплата)
Накладные создаются автоматически через Redis-событие при создании отгрузки
Топ/слабые товары — считаются по actual_qty принятых позиций, не отгруженных
