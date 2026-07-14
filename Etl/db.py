from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from a .env file

# Construct the database URL using environment variables
DataBase_URL = (
    f"postgresql://"
    f"{os.getenv('DB_USER')}:"  # Database username
    f"{os.getenv('DB_PASSWORD')}@"  # Database password
    f"{os.getenv('DB_HOST')}:"  # Database host
    f"{os.getenv('DB_PORT')}/"  # Database port
    f"{os.getenv('DB_NAME')}"  # Database name
)

# Create the SQLAlchemy engine
engine = create_engine(
    DataBase_URL,
    echo = False  # Set to True to see the generated SQL statements
)