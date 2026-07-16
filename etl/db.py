# Database connection setup using SQLAlchemy and environment variables.
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os
from etl.config import DB_PASSWORD, DB_USER, DB_HOST, DB_PORT, DB_NAME

load_dotenv() # Load environment variables from a .env file

# Construct the database URL using environment variables
# Credentials are URL-encoded since they may contain characters like '@' or ':'
DataBase_URL = (
    f"postgresql://"
    f"{quote_plus(DB_USER)}:"  # Database username
    f"{quote_plus(DB_PASSWORD)}@"  # Database password
    f"{DB_HOST}:"  # Database host
    f"{DB_PORT}/"  # Database port
    f"{DB_NAME}"  # Database name
)

# Create the SQLAlchemy engine
engine = create_engine(
    DataBase_URL,
    echo = False  # Set to True to see the generated SQL statements
)