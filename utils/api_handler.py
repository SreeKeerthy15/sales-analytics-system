import requests

def fetch_product_details(product_id):
    mock_api_data = {
        "P101": {"Category": "Electronics", "Rating": 4.5},
        "P102": {"Category": "Accessories", "Rating": 4.2},
        "P103": {"Category": "Accessories", "Rating": 4.0},
    }

    return mock_api_data.get(product_id, {"Category": "Unknown", "Rating": "N/A"})

def fetch_all_products():


    """
    Fetches all products from DummyJSON API

    Returns: list of product dictionaries
    """

    url = "https://dummyjson.com/products?limit=100"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises error for 4xx/5xx

        data = response.json()
        products = []

        for item in data.get('products', []):
            products.append({
                'id': item.get('id'),
                'title': item.get('title'),
                'category': item.get('category'),
                'brand': item.get('brand'),
                'price': item.get('price'),
                'rating': item.get('rating')
            })

        print(f"Successfully fetched {len(products)} products from API.")
        return products

    except requests.exceptions.RequestException as e:
        print("Failed to fetch products from API:", e)
        return []

def create_product_mapping(api_products):
    """
    Creates a mapping of product IDs to product info

    Parameters:
    - api_products: list of product dictionaries from fetch_all_products()

    Returns:
    - dictionary mapping product IDs to product details
    """

    product_mapping = {}

    for product in api_products:
        product_id = product.get('id')

        if product_id is None:
            continue

        product_mapping[product_id] = {
            'title': product.get('title'),
            'category': product.get('category'),
            'brand': product.get('brand'),
            'rating': product.get('rating')
        }

    return product_mapping

def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    """
    Saves enriched transactions back to file using pipe delimiter
    """

    header = [
        'TransactionID', 'Date', 'ProductID', 'ProductName',
        'Quantity', 'UnitPrice', 'CustomerID', 'Region',
        'API_Category', 'API_Brand', 'API_Rating', 'API_Match'
    ]

    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write('|'.join(header) + '\n')

            for tx in enriched_transactions:
                row = [
                    str(tx.get('TransactionID', '')),
                    str(tx.get('Date', '')),
                    str(tx.get('ProductID', '')),
                    str(tx.get('ProductName', '')),
                    str(tx.get('Quantity', '')),
                    str(tx.get('UnitPrice', '')),
                    str(tx.get('CustomerID', '')),
                    str(tx.get('Region', '')),
                    str(tx.get('API_Category', '')),
                    str(tx.get('API_Brand', '')),
                    str(tx.get('API_Rating', '')),
                    str(tx.get('API_Match', ''))
                ]

                file.write('|'.join(row) + '\n')

        print(f"Enriched sales data saved to {filename}")

    except Exception as e:
        print("Error saving enriched data:", e)

def enrich_sales_data(transactions, product_mapping):
    """
    Enriches transaction data with API product information
    Returns: list of enriched transaction dictionaries
    """

    enriched_transactions = []

    for tx in transactions:
        enriched_tx = tx.copy()

        try:
            # Extract numeric product ID (P101 -> 101)
            product_id_str = tx.get('ProductID', '')
            numeric_id = int(product_id_str.replace('P', ''))

            api_product = product_mapping.get(numeric_id)

            if api_product:
                enriched_tx['API_Category'] = api_product.get('category')
                enriched_tx['API_Brand'] = api_product.get('brand')
                enriched_tx['API_Rating'] = api_product.get('rating')
                enriched_tx['API_Match'] = True
            else:
                enriched_tx['API_Category'] = None
                enriched_tx['API_Brand'] = None
                enriched_tx['API_Rating'] = None
                enriched_tx['API_Match'] = False

        except Exception:
            enriched_tx['API_Category'] = None
            enriched_tx['API_Brand'] = None
            enriched_tx['API_Rating'] = None
            enriched_tx['API_Match'] = False

        enriched_transactions.append(enriched_tx)

    # Save to file
    save_enriched_data(enriched_transactions)

    return enriched_transactions
