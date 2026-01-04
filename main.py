from utils.file_handler import read_sales_data
from utils.data_processor import clean_and_validate_data
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data
)
from utils.report_generator import generate_sales_report


def main():
    # -------------------------------
    # PART 1: READ & CLEAN DATA
    # -------------------------------
    raw_data = read_sales_data("data/sales_data.txt")
    cleaned_data = clean_and_validate_data(raw_data)

    # -------------------------------
    # PART 3: API INTEGRATION & ENRICHMENT
    # -------------------------------
    api_products = fetch_all_products()
    product_mapping = create_product_mapping(api_products)
    enriched_transactions = enrich_sales_data(cleaned_data, product_mapping)

    # -------------------------------
    # PART 4: GENERATE FINAL REPORT
    # -------------------------------
    generate_sales_report(cleaned_data, enriched_transactions)

    print("Sales analytics pipeline completed successfully.")


if __name__ == "__main__":
    main()
