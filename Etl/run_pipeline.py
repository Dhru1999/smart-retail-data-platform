from extractor import extract_customers,extract_products,extract_orders
from logger import log

def main():

    log("Starting ETL pipeline...")

    # Call extract function from exractor.py file
    extract_customers()
    extract_products()
    extract_orders()

    log("ETL pipeline completed.")

if __name__ == "__main__":
    main()