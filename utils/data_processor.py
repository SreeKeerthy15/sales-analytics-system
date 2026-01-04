def clean_and_validate_data(raw_records):
    valid_records = []
    invalid_count = 0

    for record in raw_records:
        try:
            parts = [p.strip() for p in record.split('|')]

            if len(parts) != 8:
                invalid_count += 1
                continue

            transaction_id, date, product_id, product_name, qty, price, customer_id, region = parts

            if not transaction_id.startswith('T'):
                invalid_count += 1
                continue
            if not customer_id or not region:
                invalid_count += 1
                continue

            qty = int(qty.replace(',', ''))
            price = float(price.replace(',', ''))
            product_name = product_name.replace(',', '')

            if qty <= 0 or price <= 0:
                invalid_count += 1
                continue

            valid_records.append({
                "TransactionID": transaction_id,
                "Date": date,
                "ProductID": product_id,
                "ProductName": product_name,
                "Quantity": qty,
                "UnitPrice": price,
                "CustomerID": customer_id,
                "Region": region
            })

        except:
            invalid_count += 1

    print(f"Total records parsed: {len(raw_records)}")
    print(f"Invalid records removed: {invalid_count}")
    print(f"Valid records after cleaning: {len(valid_records)}")

    return valid_records

def parse_transactions(raw_lines):
    """
    Parses raw lines into clean list of dictionaries
    Returns: list of dictionaries with cleaned transaction data
    """

    transactions = []

    for line in raw_lines:
        # Split by pipe delimiter
        parts = [p.strip() for p in line.split('|')]

        # Skip rows with incorrect number of fields
        if len(parts) != 8:
            continue

        try:
            transaction_id, date, product_id, product_name, quantity, unit_price, customer_id, region = parts

            # Handle commas in ProductName
            product_name = product_name.replace(',', '')

            # Handle commas in numeric fields
            quantity = int(quantity.replace(',', ''))
            unit_price = float(unit_price.replace(',', ''))

            transaction = {
                'TransactionID': transaction_id,
                'Date': date,
                'ProductID': product_id,
                'ProductName': product_name,
                'Quantity': quantity,
                'UnitPrice': unit_price,
                'CustomerID': customer_id,
                'Region': region
            }

            transactions.append(transaction)

        except ValueError:
            # Skip records with conversion issues
            continue

    return transactions

def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    """
    Validates transactions and applies optional filters
    Returns: (valid_transactions, invalid_count, filter_summary)
    """

    valid_transactions = []
    invalid_count = 0

    # Collect info for display
    regions = set()
    amounts = []

    # -------------------------------
    # Step 1: Validation
    # -------------------------------
    for tx in transactions:
        try:
            # Required fields check
            required_fields = [
                'TransactionID', 'Date', 'ProductID', 'ProductName',
                'Quantity', 'UnitPrice', 'CustomerID', 'Region'
            ]

            if not all(field in tx for field in required_fields):
                invalid_count += 1
                continue

            # Business validation rules
            if tx['Quantity'] <= 0:
                invalid_count += 1
                continue

            if tx['UnitPrice'] <= 0:
                invalid_count += 1
                continue

            if not tx['TransactionID'].startswith('T'):
                invalid_count += 1
                continue

            if not tx['ProductID'].startswith('P'):
                invalid_count += 1
                continue

            if not tx['CustomerID'].startswith('C'):
                invalid_count += 1
                continue

            amount = tx['Quantity'] * tx['UnitPrice']
            regions.add(tx['Region'])
            amounts.append(amount)

            valid_transactions.append(tx)

        except Exception:
            invalid_count += 1

    # -------------------------------
    # Display available filter info
    # -------------------------------
    print("Available Regions:", sorted(regions))

    if amounts:
        print(f"Transaction Amount Range: {min(amounts)} - {max(amounts)}")
    else:
        print("Transaction Amount Range: N/A")

    # -------------------------------
    # Step 2: Filtering
    # -------------------------------
    filtered_by_region = 0
    filtered_by_amount = 0

    filtered_transactions = valid_transactions

    if region:
        before = len(filtered_transactions)
        filtered_transactions = [
            tx for tx in filtered_transactions if tx['Region'] == region
        ]
        filtered_by_region = before - len(filtered_transactions)
        print(f"Records after region filter ({region}): {len(filtered_transactions)}")

    if min_amount is not None or max_amount is not None:
        before = len(filtered_transactions)

        def amount_filter(tx):
            amount = tx['Quantity'] * tx['UnitPrice']
            if min_amount is not None and amount < min_amount:
                return False
            if max_amount is not None and amount > max_amount:
                return False
            return True

        filtered_transactions = [
            tx for tx in filtered_transactions if amount_filter(tx)
        ]

        filtered_by_amount = before - len(filtered_transactions)
        print(f"Records after amount filter: {len(filtered_transactions)}")

    # -------------------------------
    # Summary
    # -------------------------------
    filter_summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(filtered_transactions)
    }

    return filtered_transactions, invalid_count, filter_summary

def calculate_total_revenue(transactions):
    """
    Calculates total revenue from all transactions
    Returns: float
    """

    total_revenue = 0.0

    for tx in transactions:
        total_revenue += tx['Quantity'] * tx['UnitPrice']

    return round(total_revenue, 2)

def region_wise_sales(transactions):
    """
    Analyzes sales by region
    Returns: dictionary sorted by total_sales descending
    """

    region_data = {}
    total_sales_all = 0.0

    # Aggregate data
    for tx in transactions:
        region = tx['Region']
        amount = tx['Quantity'] * tx['UnitPrice']
        total_sales_all += amount

        if region not in region_data:
            region_data[region] = {
                'total_sales': 0.0,
                'transaction_count': 0
            }

        region_data[region]['total_sales'] += amount
        region_data[region]['transaction_count'] += 1

    # Calculate percentages
    for region in region_data:
        percentage = (region_data[region]['total_sales'] / total_sales_all) * 100
        region_data[region]['percentage'] = round(percentage, 2)

    # Sort by total_sales descending
    sorted_regions = dict(
        sorted(
            region_data.items(),
            key=lambda item: item[1]['total_sales'],
            reverse=True
        )
    )

    return sorted_regions

def top_selling_products(transactions, n=5):
    """
    Finds top n products by total quantity sold
    Returns: list of tuples
    """

    product_data = {}

    for tx in transactions:
        product = tx['ProductName']
        qty = tx['Quantity']
        revenue = qty * tx['UnitPrice']

        if product not in product_data:
            product_data[product] = {
                'total_quantity': 0,
                'total_revenue': 0.0
            }

        product_data[product]['total_quantity'] += qty
        product_data[product]['total_revenue'] += revenue

    # Convert to list of tuples
    product_list = [
        (product,
         data['total_quantity'],
         round(data['total_revenue'], 2))
        for product, data in product_data.items()
    ]

    # Sort by total_quantity descending
    product_list.sort(key=lambda x: x[1], reverse=True)

    return product_list[:n]

def customer_analysis(transactions):
    """
    Analyzes customer purchase patterns
    Returns: dictionary sorted by total_spent descending
    """

    customer_data = {}

    for tx in transactions:
        customer = tx['CustomerID']
        amount = tx['Quantity'] * tx['UnitPrice']
        product = tx['ProductName']

        if customer not in customer_data:
            customer_data[customer] = {
                'total_spent': 0.0,
                'purchase_count': 0,
                'products_bought': set()
            }

        customer_data[customer]['total_spent'] += amount
        customer_data[customer]['purchase_count'] += 1
        customer_data[customer]['products_bought'].add(product)

    # Final calculations
    for customer in customer_data:
        total = customer_data[customer]['total_spent']
        count = customer_data[customer]['purchase_count']

        customer_data[customer]['avg_order_value'] = round(total / count, 2)
        customer_data[customer]['total_spent'] = round(total, 2)
        customer_data[customer]['products_bought'] = list(
            customer_data[customer]['products_bought']
        )

    # Sort by total_spent descending
    sorted_customers = dict(
        sorted(
            customer_data.items(),
            key=lambda item: item[1]['total_spent'],
            reverse=True
        )
    )

    return sorted_customers

def daily_sales_trend(transactions):
    """
    Analyzes sales trends by date
    Returns: dictionary sorted by date
    """

    daily_data = {}

    for tx in transactions:
        date = tx['Date']
        amount = tx['Quantity'] * tx['UnitPrice']
        customer = tx['CustomerID']

        if date not in daily_data:
            daily_data[date] = {
                'revenue': 0.0,
                'transaction_count': 0,
                'customers': set()
            }

        daily_data[date]['revenue'] += amount
        daily_data[date]['transaction_count'] += 1
        daily_data[date]['customers'].add(customer)

    # Convert customers set to count & round revenue
    for date in daily_data:
        daily_data[date]['unique_customers'] = len(daily_data[date]['customers'])
        daily_data[date]['revenue'] = round(daily_data[date]['revenue'], 2)
        del daily_data[date]['customers']

    # Sort chronologically by date
    sorted_daily_data = dict(sorted(daily_data.items()))

    return sorted_daily_data

def find_peak_sales_day(transactions):
    """
    Identifies the date with highest revenue
    Returns: (date, revenue, transaction_count)
    """

    daily_summary = {}

    for tx in transactions:
        date = tx['Date']
        amount = tx['Quantity'] * tx['UnitPrice']

        if date not in daily_summary:
            daily_summary[date] = {
                'revenue': 0.0,
                'transaction_count': 0
            }

        daily_summary[date]['revenue'] += amount
        daily_summary[date]['transaction_count'] += 1

    # Find peak sales day
    peak_date = max(
        daily_summary.items(),
        key=lambda item: item[1]['revenue']
    )

    date = peak_date[0]
    revenue = round(peak_date[1]['revenue'], 2)
    count = peak_date[1]['transaction_count']

    return (date, revenue, count)

def low_performing_products(transactions, threshold=10):
    """
    Identifies products with low sales
    Returns: list of tuples (ProductName, TotalQuantity, TotalRevenue)
    """

    product_data = {}

    # Aggregate quantity and revenue per product
    for tx in transactions:
        product = tx['ProductName']
        qty = tx['Quantity']
        revenue = qty * tx['UnitPrice']

        if product not in product_data:
            product_data[product] = {
                'total_quantity': 0,
                'total_revenue': 0.0
            }

        product_data[product]['total_quantity'] += qty
        product_data[product]['total_revenue'] += revenue

    # Filter low-performing products
    low_products = [
        (
            product,
            data['total_quantity'],
            round(data['total_revenue'], 2)
        )
        for product, data in product_data.items()
        if data['total_quantity'] < threshold
    ]

    # Sort by TotalQuantity ascending
    low_products.sort(key=lambda x: x[1])

    return low_products
