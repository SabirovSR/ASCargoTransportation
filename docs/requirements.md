# Freight Transport Management - Requirements

## 1. Functional Requirements

### FR-AUTH: Authentication
- **FR-AUTH-01**: System must provide login via email/password
- **FR-AUTH-02**: System must support refresh sessions (maintain login on page reload)
- **FR-AUTH-03**: System must support password change by user

### FR-USER: User Management
- **FR-USER-01**: Admin must be able to create users
- **FR-USER-02**: Admin must be able to change user roles
- **FR-USER-03**: Admin must be able to deactivate users

### FR-ROUTE: Route Management
- **FR-ROUTE-01**: Users with dispatcher/admin role must be able to create routes
- **FR-ROUTE-02**: Route must contain at least 2 stops (origin, destination)
- **FR-ROUTE-03**: Each stop must have address and sequence order
- **FR-ROUTE-04**: Users must be able to view route list
- **FR-ROUTE-05**: Users must be able to search/filter routes
- **FR-ROUTE-06**: Users must be able to cancel routes (status: cancelled)

### FR-AUDIT: Audit
- **FR-AUDIT-01**: System must store route creator and creation/update timestamps
- **FR-AUDIT-02**: System must log key actions (login, create route, update route, cancel route)

## 2. Non-Functional Requirements

- **NFR-01**: API only over HTTPS (HTTP in development)
- **NFR-02**: Input validation on backend (Pydantic)
- **NFR-03**: Error handling with unified response format
- **NFR-04**: Performance - route list must return with pagination (limit/offset)
- **NFR-05**: Security - passwords only in hash (bcrypt)
- **NFR-06**: Observability (minimum): structured logs + healthcheck
- **NFR-07**: Documentation - OpenAPI available (/docs)

## 3. Business Rules

- **BR-01**: Route must have minimum 2 stops
- **BR-02**: Stop sequences must be continuous and unique within route
- **BR-03**: Cannot transition to 'active' without origin+destination
- **BR-04**: Cancelled route cannot be edited (except comment by decision)
- **BR-05**: Viewer cannot create/edit routes

## 4. Roles and Permissions (RBAC)

| Action | Admin | Dispatcher | Viewer |
|--------|-------|------------|--------|
| Create/Edit users | ✓ | ✗ | ✗ |
| Create routes | ✓ | ✓ | ✗ |
| Edit routes | ✓ | ✓ | ✗ |
| Cancel routes | ✓ | ✓ | ✗ |
| View routes | ✓ | ✓ | ✓ |

## 5. Data Model

### Users Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| full_name | VARCHAR(255) | NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| role | ENUM | admin/dispatcher/viewer |
| is_active | BOOLEAN | DEFAULT true |
| must_change_password | BOOLEAN | DEFAULT true |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

### Routes Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| route_number | VARCHAR(50) | UNIQUE, NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| status | ENUM | draft/active/completed/cancelled |
| created_by | UUID | FK -> users.id |
| planned_departure_at | TIMESTAMP | NULLABLE |
| comment | TEXT | NULLABLE |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

### Route Stops Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| route_id | UUID | FK -> routes.id (CASCADE) |
| seq | INTEGER | NOT NULL |
| type | ENUM | origin/stop/destination |
| address | TEXT | NOT NULL |
| lat | NUMERIC(10,8) | NULLABLE |
| lng | NUMERIC(11,8) | NULLABLE |
| time_window_from | TIMESTAMP | NULLABLE |
| time_window_to | TIMESTAMP | NULLABLE |
| contact_name | VARCHAR(255) | NULLABLE |
| contact_phone | VARCHAR(50) | NULLABLE |
| created_at | TIMESTAMP | NOT NULL |

## 6. Status Transitions

```
DRAFT -> ACTIVE -> COMPLETED
  |        |
  v        v
CANCELLED CANCELLED
```

- Draft: Initial state, editable
- Active: In progress, stops cannot be modified
- Completed: Finished, read-only
- Cancelled: Cancelled, read-only

## 7. Acceptance Criteria

1. ✓ User can login
2. ✓ Admin can create user and assign role
3. ✓ Dispatcher can create route with minimum 2 stops
4. ✓ Route is displayed in list and opens in details view
5. ✓ Filtering/search available by query and status
6. ✓ Route can be cancelled
7. ✓ Data persists in PostgreSQL after restart
