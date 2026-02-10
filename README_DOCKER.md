# Docker Deployment Guide

## Building Docker Image for Server Deployment

### Build and Save Image as Tar File

To build the Docker image and save it as a tar file for transfer to the server:

```bash
# Build and save as tar (uncompressed)
make docker-build-tar

# Or build, save, and compress with gzip (recommended for smaller file size)
make docker-build-tar-gz
```

This will create:
- `backend-app.tar` - Uncompressed Docker image
- `backend-app.tar.gz` - Compressed Docker image (if using gzip option)

### Transfer to Server

Copy the tar file to your server using `scp` or any file transfer method:

```bash
# For uncompressed
scp backend-app.tar user@server:/path/to/destination/

# For compressed
scp backend-app.tar.gz user@server:/path/to/destination/
```

### Load Image on Server

On the server, load the Docker image:

```bash
# For uncompressed
docker load -i backend-app.tar

# For compressed
gunzip -c backend-app.tar.gz | docker load
```

## Server Deployment

### Prerequisites

1. Docker and Docker Compose installed on the server
2. Docker image loaded (see above)
3. `.env` file configured with production settings

### Environment Configuration

Create a `.env` file on the server with the following variables:

```env
# Environment
ENVIRONMENT=production

# Security
SECRET_KEY=your-production-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your-hashed-password

# Email Settings
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-email@example.com
SMTP_PASSWORD=your-email-password

# Database Configuration
DB_TYPE=mysql  # or postgresql
DB_HOST=db  # Use service name from docker-compose
DB_PORT=3306  # 3306 for MySQL, 5432 for PostgreSQL
DB_USER=tgmi
DB_PASSWORD=tgmiadmin
DB_NAME=tgmi

# Optional: Override defaults
DB_ROOT_PASSWORD=rootpassword  # For MySQL root password
APP_PORT=8000  # Backend application port
IMAGE_NAME=backend-app  # Docker image name
IMAGE_TAG=latest  # Docker image tag
```

### Starting Services

#### For MySQL Database (Default)

```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### For PostgreSQL Database

```bash
docker-compose -f docker-compose.prod.postgres.yml up -d
```

### Managing Services

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (WARNING: deletes data)
docker-compose -f docker-compose.prod.yml down -v

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update and restart (after loading new image)
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```

### Database Migrations

After starting the services, run Alembic migrations:

```bash
# Enter the backend container
docker exec -it backend-app bash

# Run migrations
alembic upgrade head

# Exit container
exit
```

Or run migrations in one command:

```bash
docker exec -it backend-app alembic upgrade head
```

### Accessing the Application

- API: `http://your-server-ip:8000`
- API Documentation: `http://your-server-ip:8000/docs`
- API ReDoc: `http://your-server-ip:8000/redoc`

### Volume Management

Data is persisted in Docker volumes:
- `db_data` - Database data
- `uploads_data` - Uploaded files (images, documents, etc.)

To backup volumes:

```bash
# Backup database
docker run --rm -v backend-db_data:/data -v $(pwd):/backup alpine tar czf /backup/db_backup.tar.gz /data

# Backup uploads
docker run --rm -v backend-uploads_data:/data -v $(pwd):/backup alpine tar czf /backup/uploads_backup.tar.gz /data
```

## Make Commands Reference

```bash
# Build Docker image
make docker-build

# Build and save as tar
make docker-build-tar

# Build, save, and compress
make docker-build-tar-gz

# Clean Docker artifacts
make docker-clean
```
