# Freight Transport Management System

A web application for managing freight transport routes and shipments.

## Features

- **User Management**: Create and manage users with different roles (Admin, Dispatcher, Viewer)
- **Route Management**: Create, edit, and track transport routes with multiple stops
- **Authentication**: JWT-based authentication with refresh token support
- **Role-Based Access Control**: Different permissions for admins, dispatchers, and viewers

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Pydantic for validation
- JWT authentication

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- React Router
- React Query
- Zustand for state management

### Infrastructure
- Docker & Docker Compose
- Nginx

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository and navigate to the infra directory:
```bash
cd infra
```

2. Copy the example environment file:
```bash
cp .env.example .env
```

3. Start the services:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost
- API Documentation: http://localhost/docs
- Backend API: http://localhost:8000

5. Login with default credentials:
- Email: `admin@freight.local`
- Password: `admin123`

### Local Development

#### Backend

1. Navigate to the backend directory:
```bash
cd apps/backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

5. Start PostgreSQL (using Docker):
```bash
docker run -d --name freight_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=freight_db \
  -p 5432:5432 \
  postgres:15-alpine
```

6. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

1. Navigate to the frontend directory:
```bash
cd apps/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Access the frontend at http://localhost:3000

## Running Tests

### Backend Tests

```bash
cd apps/backend
pip install -r requirements.txt
pip install aiosqlite  # For SQLite testing
pytest
```

## Project Structure

```
/
├── apps/
│   ├── backend/           # FastAPI backend
│   │   ├── app/
│   │   │   ├── core/      # Config, security, logging
│   │   │   ├── db/        # Database session and base
│   │   │   ├── models/    # SQLAlchemy models
│   │   │   ├── schemas/   # Pydantic schemas
│   │   │   ├── routers/   # API endpoints
│   │   │   ├── services/  # Business logic
│   │   │   ├── repositories/  # Data access
│   │   │   └── tests/     # Tests
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── frontend/          # React frontend
│       ├── src/
│       │   ├── api/       # API client and types
│       │   ├── components/# Reusable components
│       │   ├── hooks/     # Custom hooks
│       │   ├── pages/     # Page components
│       │   ├── store/     # State management
│       │   └── styles/    # CSS styles
│       ├── Dockerfile
│       └── package.json
│
├── infra/
│   ├── docker-compose.yml
│   └── nginx.conf
│
└── docs/
    ├── api.md             # API documentation
    └── requirements.md    # Requirements specification
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user
- `POST /api/auth/change-password` - Change password

### Users (Admin only)
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `PATCH /api/users/{id}` - Update user
- `POST /api/users/{id}/reset-password` - Reset password

### Routes
- `GET /api/routes` - List routes (with filters)
- `POST /api/routes` - Create route
- `GET /api/routes/{id}` - Get route details
- `PATCH /api/routes/{id}` - Update route
- `PUT /api/routes/{id}/stops` - Update route stops
- `POST /api/routes/{id}/cancel` - Cancel route

## User Roles

| Role | Permissions |
|------|-------------|
| Admin | Full access: manage users and routes |
| Dispatcher | Create and manage routes |
| Viewer | View routes only |

## Default Admin Credentials

- Email: `admin@freight.local`
- Password: `admin123`

**⚠️ Change these credentials in production!**

## Environment Variables

### Backend
| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | - |
| SECRET_KEY | JWT secret key | - |
| DEBUG | Enable debug mode | false |
| ADMIN_EMAIL | Default admin email | admin@freight.local |
| ADMIN_PASSWORD | Default admin password | admin123 |

## License

MIT
