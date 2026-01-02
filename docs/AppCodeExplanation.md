## 1. Overview

`app.py` serves as the entry point and primary controller for the Flask web application. It handles:

* **Authentication & Session Management**: Tracking logged-in users.
* **RBAC (Role-Based Access Control)**: Using bitwise masks to manage permissions.
* **Asset Management**: CRUD operations for spaces and resources.
* **Booking Workflow**: Creation, conflict checking, and admin approval.

---

## 2. Core Logic & Decorators

### Permission System

The system uses a **bitwise mask** (stored in `user.permission_mask`) to determine user capabilities.

* **`require_perm(mask)`**: A custom decorator that wraps routes. It checks if the logged-in user's bitwise mask contains the required permission bits.
* **`has_perm` (Template Filter)**: Used in HTML templates to conditionally show or hide UI elements based on the user's permissions.

### Authentication Flow

* **`/login`**: Validates credentials using `werkzeug.security.check_password_hash`. On success, it stores the user's ID, username, and permission mask in the Flask session.
* **`/logout`**: Clears the session object to log the user out.

---

## 3. Route Categories

### User Operations (Public/General)

| Route | Method | Description |
| --- | --- | --- |
| `/` | GET | Displays all non-hidden spaces available for booking. |
| `/space/<id>` | GET | Lists specific resources (e.g., specific rooms or equipment) within a space. |
| `/book/<id>` | POST | Creates a booking request. **Includes conflict detection** to prevent overlapping "Approved" bookings. |
| `/my-bookings` | GET | Lists the current user's personal booking history and statuses. |

### Administrative Operations

These routes are protected by `@require_perm(Permission.ADMIN)`.

* **Dashboard**: `/admin/dashboard` provides an overview of all system activity.
* **Asset Management**: `/admin/assets` allows admins to create, edit, or delete **Spaces** and **Resources**.
* **Review Process**: `/admin/approve/<id>/<action>` allows admins to transition a booking between `Approved`, `Rejected`, or `Draft` states.
* **User Management**: `/admin/add_user` and `/admin/user/<id>/permissions` allow for the creation of new accounts and the adjustment of their permission masks.

---

## 4. API & Integration

* **`/api/bookings`**: Returns a JSON list of bookings.
* **Admins**: See full details (Resource + Username).
* **Regular Users**: See limited details (Resource + "Reserved") to maintain privacy while showing availability.
* **Color Coding**: Logic is included to map booking statuses (Approved, Pending, etc.) to specific hex colors for front-end calendar integration (e.g., FullCalendar).



---

## 5. Error Handling & Context

* **Global Error Handlers**: Custom handlers for `404` (Not Found) and `403` (Forbidden) ensure a consistent user experience even when errors occur.
* **Context Processor**: `inject_site_info()` automatically injects the site name and description from `.env` variables into every template rendered, avoiding repetitive code.

---

## 6. Key Configuration Values

The app relies on several environment variables for security and flexibility:

* `SECRET_KEY`: Used for signing session cookies.
* `DATABASE_URL`: Connection string for SQLAlchemy.
* `SITE_NAME`: The title used across the web interface.