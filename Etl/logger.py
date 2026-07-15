# Logger configuration for the ETL pipeline.
from datetime import datetime
import logging
from pathlib import Path

# Create a logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent.parent/"logs"
LOG_DIR.mkdir(exist_ok = True)

# Configure logging
logging.basicConfig(
    filename = LOG_DIR/"pipeline.log",
    level = logging.INFO,
    format = "%(asctime)s | %(levelname)s |%(message)s"
)

# Create a logger instance
logger = logging.getLogger(__name__) 