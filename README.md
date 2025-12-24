# Deployment Guide

## Prerequisites
- Python 3
- Docker and Docker Compose
- Git

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install Flask Flask-SQLAlchemy python-dotenv
```

### 2. Configure Environment Variables
Create a `.env` file in the project root with necessary environment variables (see ".env.example" for reference).

### 3. Set Up PostgreSQL with Docker
```yaml
version: '3.8'

services:
    db:
        image: postgres:latest
        restart: always
        environment:
            POSTGRES_USER: postgres
            POSTGRES_PASSWORD: PASSWORD
            POSTGRES_DB: booking_db
        ports:
            - "5438:5432"
        volumes:
            - db_data:/var/lib/postgresql/data

volumes:
    db_data:
```
```bash
cd database
docker-compose up -d
```

### 4. Initialize Database
```bash
python3 init_db.py
```

### 5. Run the Application
```bash
python3 app.py
```

## Environment Variables
Required variables in `.env` file:
- `SECRET_KEY`: A secret key for Flask sessions.
- `FLASK_ENV`: Set to `development` or `production`.
- `DATABASE_URL`: Database connection string. Include username, password, host, port, and database name.
- `SITE_NAME`: The name of the site.
- `SITE_DESCRIPTION`: A brief description of the site.

## Example .env File
```
SECRET_KEY=super-super-super-secret-key
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5438/booking_db

SITE_NAME=貝殼｜空間預約系統
SITE_DESCRIPTION=專屬於北科學生的空間預約平台
```

