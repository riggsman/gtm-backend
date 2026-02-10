# Database Migrations with Alembic

This project uses Alembic for database migrations to manage schema changes across different environments.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your environment:
   - Copy `env.example` to `.env`
   - Set `ENVIRONMENT` to `development`, `production`, or `live`
   - For production/live, configure database connection settings

## Database Configuration by Environment

### Development
- **Always uses SQLite**
- Database file location: `./glorious_church.db` (configurable via `SQLITE_DB_PATH`)

### Production and Live
- **Uses MySQL or PostgreSQL** (must be specified in `.env`)
- Required environment variables:
  - `DB_TYPE`: `mysql` or `postgresql`
  - `DB_HOST`: Database host
  - `DB_PORT`: Database port (optional, defaults: 3306 for MySQL, 5432 for PostgreSQL)
  - `DB_USER`: Database username
  - `DB_PASSWORD`: Database password
  - `DB_NAME`: Database name

## Running Migrations

### Create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback one migration:
```bash
alembic downgrade -1
```

### Check current revision:
```bash
alembic current
```

### View migration history:
```bash
alembic history
```

## Initial Setup

After setting up the project for the first time:

1. Ensure your `.env` file is configured
2. Run the initial migration:
   ```bash
   alembic upgrade head
   ```

This will create all database tables based on your models.

## Important Notes

- **Never edit existing migration files** - create new migrations instead
- **Always test migrations** in development before applying to production
- **Backup your database** before running migrations in production
- The `Base.metadata.create_all()` call has been removed from `main.py` - all schema changes must go through Alembic migrations
