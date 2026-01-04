from datetime import datetime
from collections import defaultdict

def generate_sales_report(transactions, enriched_transactions, output_file='output/sales_report.txt'):
    """
    Generates a comprehensive formatted sales report
    """

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_transactions = len(transactions)

    # -------------------------
    # OVERALL SUMMARY
    # -------------------------
    total_revenue = sum(tx['Quantity'] * tx['UnitPrice'] for tx in transactions)
    avg_order_value = total_revenue / total_transactions if total_transactions else 0

    dates = sorted(tx['Date'] for tx in transactions)
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"

    # -------------------------
    # REGION-WISE PERFORMANCE
    # -------------------------
    region_data = defaultdict(lambda: {'sales': 0.0, 'count': 0})

    for tx in transactions:
        amount = tx['Quantity'] * tx['UnitPrice']
        region_data[tx['Region']]['sales'] += amount
        region_data[tx['Region']]['count'] += 1

    region_rows = []
    for region, data in region_data.items():
        percent = (data['sales'] / total_revenue) * 100 if total_revenue else 0
        region_rows.append((region, data['sales'], percent, data['count']))

    region_rows.sort(key=lambda x: x[1], reverse=True)

    # -------------------------
    # TOP PRODUCTS
    # -------------------------
    product_data = defaultdict(lambda: {'qty': 0, 'rev': 0.0})
    for tx in transactions:
        product_data[tx['ProductName']]['qty'] += tx['Quantity']
        product_data[tx['ProductName']]['rev'] += tx['Quantity'] * tx['UnitPrice']

    top_products = sorted(
        product_data.items(),
        key=lambda x: x[1]['qty'],
        reverse=True
    )[:5]

    # -------------------------
    # TOP CUSTOMERS
    # -------------------------
    customer_data = defaultdict(lambda: {'spent': 0.0, 'count': 0})
    for tx in transactions:
        customer_data[tx['CustomerID']]['spent'] += tx['Quantity'] * tx['UnitPrice']
        customer_data[tx['CustomerID']]['count'] += 1

    top_customers = sorted(
        customer_data.items(),
        key=lambda x: x[1]['spent'],
        reverse=True
    )[:5]

    # -------------------------
    # DAILY SALES TREND
    # -------------------------
    daily_data = defaultdict(lambda: {'rev': 0.0, 'count': 0, 'customers': set()})
    for tx in transactions:
        amt = tx['Quantity'] * tx['UnitPrice']
        daily_data[tx['Date']]['rev'] += amt
        daily_data[tx['Date']]['count'] += 1
        daily_data[tx['Date']]['customers'].add(tx['CustomerID'])

    # -------------------------
    # PRODUCT PERFORMANCE
    # -------------------------
    best_day = max(daily_data.items(), key=lambda x: x[1]['rev'])

    low_products = [
        (p, d['qty'], d['rev'])
        for p, d in product_data.items()
        if d['qty'] < 10
    ]

    avg_region_value = {
        r: data['sales'] / data['count']
        for r, data in region_data.items()
    }

    # -------------------------
    # API ENRICHMENT SUMMARY
    # -------------------------
    enriched_success = [tx for tx in enriched_transactions if tx.get('API_Match')]
    failed_enrichment = [
        tx['ProductName'] for tx in enriched_transactions if not tx.get('API_Match')
    ]

    success_rate = (len(enriched_success) / len(enriched_transactions)) * 100 if enriched_transactions else 0

    # -------------------------
    # WRITE REPORT
    # -------------------------
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*45 + "\n")
        f.write("          SALES ANALYTICS REPORT\n")
        f.write(f"     Generated: {now}\n")
        f.write(f"     Records Processed: {total_transactions}\n")
        f.write("="*45 + "\n\n")

        f.write("OVERALL SUMMARY\n")
        f.write("-"*45 + "\n")
        f.write(f"Total Revenue:        ₹{total_revenue:,.2f}\n")
        f.write(f"Total Transactions:  {total_transactions}\n")
        f.write(f"Average Order Value: ₹{avg_order_value:,.2f}\n")
        f.write(f"Date Range:          {date_range}\n\n")

        f.write("REGION-WISE PERFORMANCE\n")
        f.write("-"*45 + "\n")
        f.write("Region     Sales           % Total   Transactions\n")
        for r, s, p, c in region_rows:
            f.write(f"{r:<10} ₹{s:>10,.2f}   {p:>6.2f}%     {c}\n")
        f.write("\n")

        f.write("TOP 5 PRODUCTS\n")
        f.write("-"*45 + "\n")
        f.write("Rank  Product          Qty   Revenue\n")
        for i, (p, d) in enumerate(top_products, 1):
            f.write(f"{i:<5} {p:<15} {d['qty']:<5} ₹{d['rev']:,.2f}\n")
        f.write("\n")

        f.write("TOP 5 CUSTOMERS\n")
        f.write("-"*45 + "\n")
        f.write("Rank  Customer   Total Spent   Orders\n")
        for i, (c, d) in enumerate(top_customers, 1):
            f.write(f"{i:<5} {c:<10} ₹{d['spent']:,.2f}   {d['count']}\n")
        f.write("\n")

        f.write("DAILY SALES TREND\n")
        f.write("-"*45 + "\n")
        f.write("Date         Revenue        Txns   Customers\n")
        for d, v in sorted(daily_data.items()):
            f.write(f"{d}  ₹{v['rev']:>10,.2f}   {v['count']:<5} {len(v['customers'])}\n")
        f.write("\n")

        f.write("PRODUCT PERFORMANCE ANALYSIS\n")
        f.write("-"*45 + "\n")
        f.write(f"Best Selling Day: {best_day[0]} (₹{best_day[1]['rev']:,.2f})\n")
        f.write("Low Performing Products:\n")
        for p, q, r in low_products:
            f.write(f"- {p}: {q} units, ₹{r:,.2f}\n")
        f.write("\n")

        f.write("API ENRICHMENT SUMMARY\n")
        f.write("-"*45 + "\n")
        f.write(f"Total Enriched: {len(enriched_success)}\n")
        f.write(f"Success Rate:  {success_rate:.2f}%\n")
        f.write("Failed Products:\n")
        for p in set(failed_enrichment):
            f.write(f"- {p}\n")

    print(f"Comprehensive sales report generated: {output_file}")
