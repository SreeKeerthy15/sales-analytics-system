from utils.file_handler import read_sales_data
from utils.data_processor import (
    parse_transactions,
    validate_and_filter,
    calculate_total_revenue,
    region_wise_sales,
    top_selling_products,
    customer_analysis,
    daily_sales_trend,
    find_peak_sales_day,
    low_performing_products
)
from utils.api_handler import (
    fetch_all_products,
    create_product_mapping,
    enrich_sales_data
)
from utils.report_generator import generate_sales_report


def main():
    """
    Main execution function for Sales Analytics System
    """

    try:
        print("=" * 40)
        print("        SALES ANALYTICS SYSTEM")
        print("=" * 40)

        # -------------------------------------------------
        # 1. Read sales data
        # -------------------------------------------------
        print("\n[1/10] Reading sales data...")
        raw_lines = read_sales_data("data/sales_data.txt")
        print(f"✓ Successfully read {len(raw_lines)} transactions")

        # -------------------------------------------------
        # 2. Parse and clean
        # -------------------------------------------------
        print("\n[2/10] Parsing and cleaning data...")
        transactions = parse_transactions(raw_lines)
        print(f"✓ Parsed {len(transactions)} records")

        # -------------------------------------------------
        # 3. Display filter options
        # -------------------------------------------------
        print("\n[3/10] Filter Options Available:")

        regions = sorted(set(tx['Region'] for tx in transactions))
        amounts = [tx['Quantity'] * tx['UnitPrice'] for tx in transactions]

        print("Regions:", ", ".join(regions))
        print(f"Amount Range: ₹{min(amounts):,.0f} - ₹{max(amounts):,.0f}")

        apply_filter = input("\nDo you want to filter data? (y/n): ").strip().lower()

        region_filter = None
        min_amt = None
        max_amt = None

        if apply_filter == 'y':
            region_filter = input("Enter region (or press Enter to skip): ").strip()
            if not region_filter:
                region_filter = None

            min_val = input("Enter minimum amount (or press Enter to skip): ").strip()
            max_val = input("Enter maximum amount (or press Enter to skip): ").strip()

            min_amt = float(min_val) if min_val else None
            max_amt = float(max_val) if max_val else None

        # -------------------------------------------------
        # 4. Validate and filter
        # -------------------------------------------------
        print("\n[4/10] Validating transactions...")
        valid_transactions, invalid_count, summary = validate_and_filter(
            transactions,
            region=region_filter,
            min_amount=min_amt,
            max_amount=max_amt
        )

        print(f"✓ Valid: {summary['final_count']} | Invalid: {invalid_count}")

        # -------------------------------------------------
        # 5. Analysis
        # -------------------------------------------------
        print("\n[5/10] Analyzing sales data...")
        total_revenue = calculate_total_revenue(valid_transactions)
        region_stats = region_wise_sales(valid_transactions)
        top_products = top_selling_products(valid_transactions)
        customers = customer_analysis(valid_transactions)
        daily_trend = daily_sales_trend(valid_transactions)
        peak_day = find_peak_sales_day(valid_transactions)
        low_products = low_performing_products(valid_transactions)
        print("✓ Analysis complete")

        # -------------------------------------------------
        # 6. Fetch API data
        # -------------------------------------------------
        print("\n[6/10] Fetching product data from API...")
        api_products = fetch_all_products()
        print(f"✓ Fetched {len(api_products)} products")

        # -------------------------------------------------
        # 7. Enrich data
        # -------------------------------------------------
        print("\n[7/10] Enriching sales data...")
        product_mapping = create_product_mapping(api_products)
        enriched_transactions = enrich_sales_data(valid_transactions, product_mapping)

        enriched_count = sum(1 for tx in enriched_transactions if tx.get('API_Match'))
        success_rate = (enriched_count / len(enriched_transactions)) * 100 if enriched_transactions else 0

        print(f"✓ Enriched {enriched_count}/{len(enriched_transactions)} transactions ({success_rate:.1f}%)")

        # -------------------------------------------------
        # 8. Saving already handled in enrichment
        # -------------------------------------------------
        print("\n[8/10] Saving enriched data...")
        print("✓ Saved to: data/enriched_sales_data.txt")

        # -------------------------------------------------
        # 9. Generate report
        # -------------------------------------------------
        print("\n[9/10] Generating report...")
        generate_sales_report(valid_transactions, enriched_transactions)
        print("✓ Report saved to: output/sales_report.txt")

        # -------------------------------------------------
        # 10. Completion
        # -------------------------------------------------
        print("\n[10/10] Process Complete!")
        print("=" * 40)

    except Exception as e:
        print("\n❌ An error occurred while running the system.")
        print("Error details:", e)
        print("Please check your input files or configuration.")


if __name__ == "__main__":
    main()
