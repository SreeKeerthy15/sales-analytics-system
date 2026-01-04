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
