from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
import os

from sql_helper import SqlHelper

def get_database_url():
    """
    Get database URL based on environment.
    - Development: Always uses SQLite
    - Production/Live: Uses MySQL or PostgreSQL based on DB_TYPE in env
    """
    environment = settings.ENVIRONMENT.lower()
    
    # Development always uses SQLite
    if environment == "development":
        db_path = settings.SQLITE_DB_PATH
        # Ensure directory exists for SQLite
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        return f"sqlite:///{db_path}"
    
    # Production and Live use MySQL or PostgreSQL
    if environment in ["production", "live"]:
        db_type = settings.DB_TYPE
        if not db_type:
            raise ValueError(
                f"DB_TYPE must be set in .env for {environment} environment. "
                "Must be 'mysql' or 'postgresql'"
            )
        
        db_type = db_type.lower()
        if db_type not in ["mysql", "postgresql"]:
            raise ValueError(
                f"DB_TYPE must be 'mysql' or 'postgresql', got '{db_type}'"
            )
        
        # Validate required database connection parameters
        required_params = ["DB_HOST", "DB_USER",  "DB_NAME"]  #"DB_PASSWORD",
        missing_params = [param for param in required_params if not getattr(settings, param, None)]
        if missing_params:
            raise ValueError(
                f"Missing required database parameters for {environment}: {', '.join(missing_params)}"
            )
        SqlHelper.create_user_and_grant_privileges(settings.DB_USER,settings.DB_PASSWORD,settings.DB_NAME)
        db_host = settings.DB_HOST
        db_port = settings.DB_PORT or (3306 if db_type == "mysql" else 5432)
        db_user = settings.DB_USER
        # db_password = settings.DB_PASSWORD
        db_name = settings.DB_NAME
        
        from urllib.parse import quote_plus

        db_password = quote_plus(settings.DB_PASSWORD)
        if db_type == "mysql":
            # MySQL connection string
            return f"mysql+pymysql://{db_user}:@{db_host}:{db_port}/{db_name}"
        else:  # postgresql
            # PostgreSQL connection string
            return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Fallback to SQLite for unknown environments
    return f"sqlite:///{settings.SQLITE_DB_PATH}"

SQLALCHEMY_DATABASE_URL = get_database_url()

# Create engine with appropriate connect_args
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # For MySQL and PostgreSQL, we might want to set pool settings
    connect_args = {
        # "pool_pre_ping": True,  # Verify connections before using
        # "pool_recycle": 3600,   # Recycle connections after 1 hour
    }

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args=connect_args,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping = True,
    pool_recycle = 3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
