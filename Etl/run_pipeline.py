from Etl.loader import load_dataframe
from extractor import extract_customers,extract_products,extract_orders
from logger import log
from transformer import transform_customer,convert_price

def main():

    log("Starting ETL pipeline...")

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
    
    log("ETL pipeline completed.")

if __name__ == "__main__":
    main()