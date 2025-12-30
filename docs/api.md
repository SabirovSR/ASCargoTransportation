# Freight Transport Management API

## Overview

RESTful API for managing freight transport routes and users.

Base URL: `/api`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Login

```
POST /api/auth/login
```

Request body:
```json
{
  "email": "admin@freight.local",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "admin@freight.local",
    "full_name": "System Admin",
    "role": "admin",
    "is_active": true,
    "must_change_password": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### Refresh Token

```
POST /api/auth/refresh
```

Request body:
```json
{
  "refresh_token": "eyJ..."
}
```

### Logout

```
POST /api/auth/logout
```

Request body:
```json
{
  "refresh_token": "eyJ..."
}
```

### Get Current User

```
GET /api/auth/me
Authorization: Bearer <access_token>
```

### Change Password

```
POST /api/auth/change-password
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

## Users (Admin only)

### List Users

```
GET /api/users?limit=20&offset=0
Authorization: Bearer <access_token>
```

### Create User

```
POST /api/users
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "password123",
  "role": "dispatcher"
}
```

### Update User

```
PATCH /api/users/{user_id}
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "full_name": "Jane Doe",
  "role": "admin",
  "is_active": true
}
```

### Reset User Password

```
POST /api/users/{user_id}/reset-password
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "new_password": "newpassword123"
}
```

## Routes

### List Routes

```
GET /api/routes?limit=20&offset=0&status=draft&q=search
Authorization: Bearer <access_token>
```

Query parameters:
- `limit` (int): Number of items per page (default: 20)
- `offset` (int): Number of items to skip (default: 0)
- `status` (string): Filter by status (draft, active, completed, cancelled)
- `q` (string): Search by route number or title
- `created_by` (uuid): Filter by creator
- `from` (datetime): Filter by creation date (from)
- `to` (datetime): Filter by creation date (to)

### Get Route

```
GET /api/routes/{route_id}
Authorization: Bearer <access_token>
```

### Create Route

```
POST /api/routes
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "title": "Moscow - Saint Petersburg",
  "route_number": null,
  "planned_departure_at": "2024-01-15T08:00:00Z",
  "comment": "Express delivery",
  "stops": [
    {
      "seq": 1,
      "type": "origin",
      "address": "Moscow, Red Square 1",
      "contact_name": "Ivan Petrov",
      "contact_phone": "+7 999 123 4567"
    },
    {
      "seq": 2,
      "type": "destination",
      "address": "Saint Petersburg, Nevsky Prospekt 1",
      "contact_name": "Maria Ivanova",
      "contact_phone": "+7 999 765 4321"
    }
  ]
}
```

### Update Route

```
PATCH /api/routes/{route_id}
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "title": "Updated Title",
  "comment": "Updated comment",
  "status": "active"
}
```

### Update Route Stops

```
PUT /api/routes/{route_id}/stops
Authorization: Bearer <access_token>
```

Request body:
```json
{
  "stops": [
    {
      "seq": 1,
      "type": "origin",
      "address": "New Moscow Address"
    },
    {
      "seq": 2,
      "type": "stop",
      "address": "Intermediate Stop"
    },
    {
      "seq": 3,
      "type": "destination",
      "address": "New Destination"
    }
  ]
}
```

### Cancel Route

```
POST /api/routes/{route_id}/cancel
Authorization: Bearer <access_token>
```

## Error Response Format

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

Error codes:
- `VALIDATION_ERROR` (422)
- `AUTHENTICATION_ERROR` (401)
- `AUTHORIZATION_ERROR` (403)
- `NOT_FOUND` (404)
- `CONFLICT` (409)
- `BUSINESS_RULE_ERROR` (400)
- `INTERNAL_ERROR` (500)

## Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## OpenAPI Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`
