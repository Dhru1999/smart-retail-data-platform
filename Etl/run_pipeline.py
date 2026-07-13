from extractor import extract_customers,extract_products,extract_orders
from logger import log

def main():

    log("Starting ETL pipeline...")

    # Call extract function from exractor.py file
    customers =extract_customers()
    products = extract_products()
    orders = extract_orders()

    print("\nCustomers Data:")
    print(customers)
    
    print("\nProducts Data:")
    print(products)
    
    print("\nOrders Data:")
    print(orders)
    
    log("ETL pipeline completed.")

if __name__ == "__main__":
    main()