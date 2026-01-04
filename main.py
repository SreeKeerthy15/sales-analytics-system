from utils.file_handler import read_sales_data
from utils.data_processor import clean_and_validate_data
from utils.api_handler import fetch_product_details

from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data
)


def main():
    raw_data = read_sales_data("data/sales_data.txt")
    cleaned_data = clean_and_validate_data(raw_data)

        # --- PART 3: API INTEGRATION & ENRICHMENT ---

    api_products = fetch_all_products()
    product_mapping = create_product_mapping(api_products)
    enriched_transactions = enrich_sales_data(cleaned_data, product_mapping)


    total_revenue = 0
    region_sales = {}

    for record in cleaned_data:
        revenue = record["Quantity"] * record["UnitPrice"]
        total_revenue += revenue

        region = record["Region"]
        region_sales[region] = region_sales.get(region, 0) + revenue

        product_info = fetch_product_details(record["ProductID"])
        record.update(product_info)

    with open("output/sales_report.txt", "w") as report:
        report.write(f"Total Revenue: {total_revenue}\n")
        report.write("Revenue by Region:\n")
        for region, value in region_sales.items():
            report.write(f"{region}: {value}\n")

    print("Sales report generated successfully.")

if __name__ == "__main__":
    main()
