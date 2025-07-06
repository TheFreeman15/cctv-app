# CCTV-APP

The backend system for managing users and cameras in a CCTV monitoring application.

---

## 🛠 Tools Used

- **MySQL** – Stores user and camera data  
- **Redis** – Stores access and refresh token data  
- **FastAPI** – Core web framework for API endpoints  
- **phpMyAdmin** – GUI to view and manage MySQL data  

---

## 🗃 Database Design

The system uses 7 tables:

1. **Users** – User details and hashed passwords  
2. **user_role_map** – One-to-one mapping of users to roles  
3. **Roles** – Contains role types (Superadmin, Branchadmin, etc.)  
4. **role_permission_map** – Many-to-many mapping of roles to permissions  
5. **Permissions** – Defined actions (e.g., `CREATE_USER`, `DELETE_USER`)  
6. **Cameras** – Cameras and their associated details  
7. **camera_assignment_map** – Many-to-many mapping of cameras to users  

> 📊 _[Insert schema/image visualization here]_

A seed script is available at `sql/001_init_schema.sql`. This sets up all required schema and the first superadmin. It only runs during the first setup.

---

## 📦 Backend Structure

Modules:

- `application/authentication.py` – Authentication logic  
- `application/service.py` – Permission management + activity logging  
- `application/user_management.py` – User CRUD logic  
- `application/camera_management.py` – Camera CRUD logic  
- `application/api/v1.py` – Route definitions  

---

## 🔐 Authentication

### Login Flow

- Authenticate with email + password  
- On success:
  - Access Token (short-lived)
  - Refresh Token (longer-lived)  
- Tokens are stored in Redis  
- Access tokens can be renewed using the refresh token  

### Token Decorator

- All endpoints use the decorator `@LoginHandler.authenticate_user`  
- It validates the access token before allowing execution

---

## 🔑 Permission Management

- Each API has a permission identifier  
- Permissions are mapped to Roles  
- Roles are mapped to Users  
- When a request is made, system checks if user has permission via DB mappings  
- Permissions are **dynamic** – can be added or modified without code changes

---

## 👤 User Management

- Standard CRUD APIs  
- Permission required: `VIEW_ALL_USERS`, `CREATE_USER`, `EDIT_USER`, `DELETE_USER`  
- Only Superadmin has full access by default

---

## 🎥 Camera Management

- Standard CRUD APIs  
- Permission required: `VIEW_CAMERA`, `CREATE_CAMERA`, `EDIT_CAMERA`, `DELETE_CAMERA`  
- Only Superadmin and Branchadmin can create/assign cameras  
- Branchadmin cannot delete cameras created by Superadmin  
  - **Rank-based protection**:
    - Lower-ranked users cannot modify higher-ranked users' resources  
    - e.g. Superadmin = rank 1, Branchadmin = rank 2

---

## 📝 Activity Logging

- Every `create`, `update`, `delete` action is logged  
- Logs include:
  - Action type
  - Who performed the action
  - Target of the action (e.g., "Superadmin deleted camera1")

---

## 🚀 Deployment Strategy

The project includes a `docker-compose.yml` file with the following services:

1. **Network** – Creates a `shared-net` for inter-container communication  
2. **MySQL** – Runs MySQL + mounts initial SQL seed scripts  
3. **Redis** – Token store  
4. **phpMyAdmin** – GUI for MySQL  
5. **FastAPI backend** – Builds and runs FastAPI app in a container

---

## 📦 Requirements

- Docker  
- Docker Compose  

---

## 🔧 How to Deploy

```bash
# Clone the repository
git clone <repo-url>
cd <project-directory>

# Build and start all services
docker-compose up -d --build
