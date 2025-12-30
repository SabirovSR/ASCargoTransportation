# АС "Судоперевозки"

Веб-приложение для управления маршрутами судоперевозок и отправками.

## Возможности

- **Управление пользователями**: Создание и управление пользователями с различными ролями (Администратор, Диспетчер, Наблюдатель)
- **Управление маршрутами**: Создание, редактирование и отслеживание транспортных маршрутов с несколькими остановками
- **Аутентификация**: JWT-аутентификация с поддержкой refresh-токенов
- **Контроль доступа на основе ролей**: Различные права доступа для администраторов, диспетчеров и наблюдателей

## Технологический стек

### Backend
- Python
- FastAPI
- SQLAlchemy 2.0 (асинхронный)
- PostgreSQL
- Pydantic для валидации
- JWT аутентификация

### Frontend
- React 
- TypeScript
- Tailwind CSS
- React Router
- React Query
- Zustand для управления состоянием

### Инфраструктура
- Docker & Docker Compose
- Nginx

## Быстрый старт

### Использование Docker Compose (Рекомендуется)

1. Клонируйте репозиторий и перейдите в директорию infra:
```bash
cd infra
```

2. Скопируйте файл с примером переменных окружения:
```bash
cp .env.example .env
```

3. Запустите сервисы:
```bash
docker-compose up -d
```

4. Доступ к приложению:
- Frontend: http://localhost
- Документация API: http://localhost/docs
- Backend API: http://localhost:8000

5. Войдите используя данные по умолчанию:
- Email: `admin@freight.local`
- Пароль: `admin123`

### Локальная разработка

#### Backend

1. Перейдите в директорию backend:
```bash
cd apps/backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # В Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения:
```bash
cp .env.example .env
```

5. Запустите PostgreSQL (используя Docker):
```bash
docker run -d --name freight_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=freight_db \
  -p 5432:5432 \
  postgres:15-alpine
```

6. Запустите backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

1. Перейдите в директорию frontend:
```bash
cd apps/frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите сервер разработки:
```bash
npm run dev
```

4. Откройте frontend по адресу http://localhost:3000

## Запуск тестов

### Тесты Backend

```bash
cd apps/backend
pip install -r requirements.txt
pip install aiosqlite  # Для тестирования с SQLite
pytest
```

## Структура проекта

```
/
├── apps/
│   ├── backend/           # Backend на FastAPI
│   │   ├── app/
│   │   │   ├── core/      # Конфигурация, безопасность, логирование
│   │   │   ├── db/        # Сессия БД и базовые классы
│   │   │   ├── models/    # Модели SQLAlchemy
│   │   │   ├── schemas/   # Схемы Pydantic
│   │   │   ├── routers/   # API эндпоинты
│   │   │   ├── services/  # Бизнес-логика
│   │   │   ├── repositories/  # Доступ к данным
│   │   │   └── tests/     # Тесты
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── frontend/          # Frontend на React
│       ├── src/
│       │   ├── api/       # API клиент и типы
│       │   ├── components/# Переиспользуемые компоненты
│       │   ├── hooks/     # Пользовательские хуки
│       │   ├── pages/     # Компоненты страниц
│       │   ├── store/     # Управление состоянием
│       │   └── styles/    # CSS стили
│       ├── Dockerfile
│       └── package.json
│
├── infra/
│   ├── docker-compose.yml
│   └── nginx.conf
│
└── docs/
    ├── api.md             # Документация API
    └── requirements.md    # Спецификация требований
```

## API эндпоинты

### Аутентификация
- `POST /api/auth/login` - Вход в систему
- `POST /api/auth/refresh` - Обновить токен
- `POST /api/auth/logout` - Выход из системы
- `GET /api/auth/me` - Получить текущего пользователя
- `POST /api/auth/change-password` - Изменить пароль

### Пользователи (Только для администратора)
- `GET /api/users` - Список пользователей
- `POST /api/users` - Создать пользователя
- `PATCH /api/users/{id}` - Обновить пользователя
- `POST /api/users/{id}/reset-password` - Сбросить пароль

### Маршруты
- `GET /api/routes` - Список маршрутов (с фильтрами)
- `POST /api/routes` - Создать маршрут
- `GET /api/routes/{id}` - Получить детали маршрута
- `PATCH /api/routes/{id}` - Обновить маршрут
- `PUT /api/routes/{id}/stops` - Обновить остановки маршрута
- `POST /api/routes/{id}/cancel` - Отменить маршрут

## Роли пользователей

| Роль | Права доступа |
|------|-------------|
| Администратор | Полный доступ: управление пользователями и маршрутами |
| Диспетчер | Создание и управление маршрутами |
| Наблюдатель | Только просмотр маршрутов |

## Учётные данные администратора по умолчанию

- Email: `admin@freight.local`
- Пароль: `admin123`

**⚠️ Измените эти данные в production окружении!**

## Переменные окружения

### Backend
| Переменная | Описание | По умолчанию |
|----------|-------------|---------|
| DATABASE_URL | Строка подключения к PostgreSQL | - |
| SECRET_KEY | Секретный ключ для JWT | - |
| DEBUG | Включить режим отладки | false |
| ADMIN_EMAIL | Email администратора по умолчанию | admin@freight.local |
| ADMIN_PASSWORD | Пароль администратора по умолчанию | admin123 |

## Лицензия

MIT
