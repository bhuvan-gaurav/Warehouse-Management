# Warehouse Dispatch Management System

## 1. Problem Statement

A logistics company operates a warehouse where packages arrive from different sources and need to be dispatched to various destinations.

Warehouse staff need to organize packages, track their current status, and group them into dispatch batches before assigning them to delivery vehicles.

Currently, these operations are handled manually, making it difficult to track pending packages, manage dispatches, and monitor warehouse activity.

The goal is to build a **Warehouse Dispatch Management System** that simplifies package management and provides visibility into warehouse dispatch operations.

## 2. Objectives

- Register and maintain package details.
- Track the status of packages inside the warehouse.
- Search and filter packages based on different criteria.
- Organize packages into dispatch batches.
- View dispatch information and warehouse statistics.

## 3. Functional Requirements

### Package Management

- Register a new package with details such as package name, destination, weight, arrival date and status.
- View the details of a specific package.
- Update package information partially.
- Delete a package if it has not yet been dispatched.
- Retrieve packages using filters such as destination, status and arrival date.

### Dispatch Management

- View dispatch batches with filters such as destination, vehicle and dispatch status.

### Warehouse Analytics

Generate a dispatch summary containing:

- Total packages received.
- Total packages pending dispatch.
- Total packages dispatched.
- Destination-wise package count.

## 4. API Requirements

The application must provide APIs for the following. Fill in the API contract for each row.

| # | Description | Method | Endpoint | Path / Query Params | Request Body | Response Body | Status Codes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Register a package | POST | `/packages` | Header: `token` (optional) | `PackageCreate` | `PackageResponse` | 201 |
| 2 | Get the details of a specific package | GET | `/packages/{id}` | Path: `id` (int) | None | `PackageResponse` | 200, 404 |
| 3 | Partially update package details | PATCH | `/packages/{id}` | Path: `id` (int) | `PackageUpdate` | `PackageResponse` | 200, 404 |
| 4 | Delete a package (only if it has not been dispatched) | DELETE | `/packages/{id}` | Path: `id` (int) | None | `MessageResponse` | 200, 400, 404 |
| 5 | Search and filter packages (by destination, status, arrival date) | GET | `/packages` | Query: `destination`, `status`, `arrival_date`, Header: `token` | None | `List[PackageResponse]` | 200, 401 |
| 6 | View dispatch batches (filter by destination, vehicle, dispatch status) | GET | `/dispatch_batches` | Query: `destination`, `vehicle_number`, `status`, Header: `token` | None | `List[DispatchBatchResponse]` | 200, 401 |
| 7 | Get warehouse statistics (dispatch summary) | GET | `/packages/status` | None | None | `WarehouseSummaryResponse` | 200 |
| 8 | Add data manually (e.g. create a dispatch batch and assign packages) | POST | `/dispatch_batches` | None | `DispatchBatchCreate` | `DispatchBatchResponse` | 201 |

> **Your task:** Complete the table before you start building. For each API, decide the HTTP method, endpoint path, path and query parameters, request body, response body, and status codes — including error cases (e.g. package not found, deleting a dispatched package).

> **Note:** To have data to work with, your app needs an endpoint to add data manually (row 8) — the other requirements only cover viewing dispatch batches, not creating them.

## 5. Scope

The application will focus on warehouse package management and dispatch visibility.

The following are **outside the scope**:

- User authentication and authorization.
- Live vehicle tracking.
- Route optimization.
- Payment processing.
- External logistics integrations.

## 6. Technology Stack

| Area | Technology |
| --- | --- |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| API Documentation | Swagger UI |
| API Testing | Postman |

## 7. Expected Outcome

A working REST API application that allows warehouse staff to manage packages, view dispatch batches, filter records and generate basic warehouse statistics.

---

## 8. Security & Architecture Features

### 1. JWT (JSON Web Tokens)
- **RFC 7519 / RFC 7518 (HS256)** compliant token generation and signature verification.
- Separate **Access Tokens** (60 minutes) and **Refresh Tokens** (7 days).
- Token payload embeds identity (`sub`) and RBAC role (`role`).
- Integrated with FastAPI's `HTTPBearer`, enabling the Swagger UI "Authorize" button and standard `Authorization: Bearer <token>` headers.

### 2. Password Hashing (Argon2)
- State-of-the-art password hashing using **Argon2id** (`argon2-cffi`).
- Passwords are salted and hashed upon registration (`/register`).
- Constant-time verification on login (`/login`) prevents timing attacks.
- Passwords are never returned in responses or exposed in schemas.

### 3. Pydantic Validation
- Strict request data validation with Pydantic v2 in `schemas.py`:
  - `PackageCreate`: Requires `name`, `destination`, and positive `weight > 0`.
  - `PackageUpdate`: Partial payload validation using `exclude_unset=True`.
  - `DispatchBatchCreate`: Validates destination, vehicle number, and package IDs.
  - `UserRegister`: Enforces minimum length for username and password with `UserRole` enum.
- Response models (`PackageResponse`, `DispatchBatchResponse`, `WarehouseSummaryResponse`, `UserResponse`, etc.) sanitize and standardize all API responses.

### 4. RBAC (Role-Based Access Control)
Three hierarchical roles are enforced across endpoints via dependency injection in `auth.py`:

| Role | Permissions |
| :--- | :--- |
| **`admin`** | Full system access: register packages, view/update packages, delete packages, create dispatch batches, view batches, view analytics, and manage users (`GET /users`). |
| **`manager`** | Dispatch operations: create dispatch batches (`POST /dispatch_batches`), register packages, view/update packages, view analytics. Cannot delete packages or manage users. |
| **`staff`** | Package handling: register packages (`POST /packages`), partially update packages (`PATCH /packages/{id}`), view packages, view batches, and view analytics. Cannot create dispatch batches or delete packages. |

