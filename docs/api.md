# API АС "Грузоперевозки"

## Обзор

RESTful API для управления маршрутами грузоперевозок и пользователями.

Базовый URL: `/api`

## Аутентификация

API использует JWT (JSON Web Tokens) для аутентификации.

### Вход в систему

```
POST /api/auth/login
```

Тело запроса:
```json
{
  "email": "admin@freight.local",
  "password": "admin123"
}
```

Ответ:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "admin@freight.local",
    "full_name": "Системный администратор",
    "role": "admin",
    "is_active": true,
    "must_change_password": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### Обновление токена

```
POST /api/auth/refresh
```

Тело запроса:
```json
{
  "refresh_token": "eyJ..."
}
```

### Выход из системы

```
POST /api/auth/logout
```

Тело запроса:
```json
{
  "refresh_token": "eyJ..."
}
```

### Получить текущего пользователя

```
GET /api/auth/me
Authorization: Bearer <access_token>
```

### Изменить пароль

```
POST /api/auth/change-password
Authorization: Bearer <access_token>
```

Тело запроса:
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

## Пользователи (Только для администратора)

### Список пользователей

```
GET /api/users?limit=20&offset=0
Authorization: Bearer <access_token>
```

### Создать пользователя

```
POST /api/users
Authorization: Bearer <access_token>
```

Тело запроса:
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "password123",
  "role": "dispatcher"
}
```

### Обновить пользователя

```
PATCH /api/users/{user_id}
Authorization: Bearer <access_token>
```

Тело запроса:
```json
{
  "full_name": "Иван Иванов",
  "role": "admin",
  "is_active": true
}
```

### Сбросить пароль пользователя

```
POST /api/users/{user_id}/reset-password
Authorization: Bearer <access_token>
```

Тело запроса:
```json
{
  "new_password": "newpassword123"
}
```

## Маршруты

### Список маршрутов

```
GET /api/routes?limit=20&offset=0&status=draft&q=search
Authorization: Bearer <access_token>
```

Параметры запроса:
- `limit` (int): Количество элементов на странице (по умолчанию: 20)
- `offset` (int): Количество элементов для пропуска (по умолчанию: 0)
- `status` (string): Фильтр по статусу (draft, active, completed, cancelled)
- `q` (string): Поиск по номеру или названию маршрута
- `created_by` (uuid): Фильтр по создателю
- `from` (datetime): Фильтр по дате создания (с)
- `to` (datetime): Фильтр по дате создания (до)

### Получить маршрут

```
GET /api/routes/{route_id}
Authorization: Bearer <access_token>
```

### Создать маршрут

```
POST /api/routes
Authorization: Bearer <access_token>
```

Тело запроса:
```json
{
  "title": "Москва - Санкт-Петербург",
  "route_number": null,
  "planned_departure_at": "2024-01-15T08:00:00Z",
  "comment": "Экспресс-доставка",
  "stops": [
    {
      "seq": 1,
      "type": "origin",
      "address": "Москва, Красная площадь 1",
      "contact_name": "Иван Петров",
      "contact_phone": "+7 999 123 4567"
    },
    {
      "seq": 2,
      "type": "destination",
      "address": "Санкт-Петербург, Невский проспект 1",
      "contact_name": "Мария Иванова",
      "contact_phone": "+7 999 765 4321"
    }
  ]
}
```

### Обновить маршрут

```
PATCH /api/routes/{route_id}
Authorization: Bearer <access_token>
```

Тело запроса:
```json
{
  "title": "Обновлённое название",
  "comment": "Обновлённый комментарий",
  "status": "active"
}
```

### Обновить остановки маршрута

```
PUT /api/routes/{route_id}/stops
Authorization: Bearer <access_token>
```

Тело запроса:
```json
{
  "stops": [
    {
      "seq": 1,
      "type": "origin",
      "address": "Новый адрес в Москве"
    },
    {
      "seq": 2,
      "type": "stop",
      "address": "Промежуточная остановка"
    },
    {
      "seq": 3,
      "type": "destination",
      "address": "Новый пункт назначения"
    }
  ]
}
```

### Отменить маршрут

```
POST /api/routes/{route_id}/cancel
Authorization: Bearer <access_token>
```

## Формат ответа с ошибкой

Все ошибки следуют единому формату:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Читаемое человеком сообщение",
    "details": [
      {
        "field": "email",
        "message": "Неверный формат email"
      }
    ]
  }
}
```

Коды ошибок:
- `VALIDATION_ERROR` (422) - Ошибка валидации
- `AUTHENTICATION_ERROR` (401) - Ошибка аутентификации
- `AUTHORIZATION_ERROR` (403) - Ошибка авторизации
- `NOT_FOUND` (404) - Не найдено
- `CONFLICT` (409) - Конфликт
- `BUSINESS_RULE_ERROR` (400) - Ошибка бизнес-правила
- `INTERNAL_ERROR` (500) - Внутренняя ошибка

## Проверка работоспособности

```
GET /health
```

Ответ:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Документация OpenAPI

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`
