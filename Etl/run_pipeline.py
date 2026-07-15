# Orchestrates the ETL pipeline by calling the extract, transform, and load functions in sequence.
from venv import logger
from Etl.loader import load_dataframe
from extractor import extract_customers,extract_products,extract_orders
from transformer import transform_customer,convert_price

def main():
    try:
        logger.info("Starting ETL pipeline...")
        # Call extract function from exractor.py file
        customers = extract_customers()
        # Call tranform function from transformer.py file
        clean_customers = transform_customer(customers)
        # print(clean_customers)

        # Call load function from loader.py file
        load_dataframe(
            clean_customers,
            table_name = "customers"
        )

        products = extract_products()
        orders = extract_orders()

        # Call tranform function from transformer.py file
        products = convert_price(products)
        orders = convert_price(orders)
        
        # Call load function from loader.py file
        load_dataframe(
            products,
            table_name = "products"
        )
        # Call load function from loader.py file
        load_dataframe(
            orders,
            table_name = "orders"
        )
        logger.info("ETL pipeline completed.")
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        raise e

# Entry point for the script
if __name__ == "__main__":
    main()