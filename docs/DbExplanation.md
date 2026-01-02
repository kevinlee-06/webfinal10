# Database Schema
## Models
### User
- **Table Name**: `users`
- **Fields**:
    - `id`: Integer, Primary Key
    - `username`: String(50), Unique, Not Null
    - `password_hash`: String(256), Not Null
    - `permission_mask`: Integer, Default 4

### Space
- **Table Name**: `spaces`
- **Fields**:
    - `id`: Integer, Primary Key
    - `name`: String(100), Not Null
    - `description`: Text
    - `image_url`: String(255)
    - `is_hidden`: Boolean, Default False
- **Relationships**: 
    - Resources (One-to-Many)

### Resource
- **Table Name**: `resources`
- **Fields**:
    - `id`: Integer, Primary Key
    - `space_id`: Integer, Foreign Key (spaces.id), Not Null
    - `name`: String(100), Not Null
    - `resource_type`: String(50)
    - `description`: Text
    - `image_url`: String(255)
    - `is_hidden`: Boolean, Default False

### Booking
- **Table Name**: `bookings`
- **Fields**:
    - `id`: Integer, Primary Key
    - `user_id`: Integer, Foreign Key (users.id), Not Null
    - `resource_id`: Integer, Foreign Key (resources.id), Not Null
    - `start_time`: DateTime, Not Null
    - `end_time`: DateTime, Not Null
    - `attendees`: Integer, Default 1
    - `status`: String(20), Default 'Pending'
    - `created_at`: DateTime, Default Current UTC Time
- **Relationships**:
    - User (Many-to-One)
    - Resource (Many-to-One)