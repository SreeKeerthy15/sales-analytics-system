def fetch_product_details(product_id):
    mock_api_data = {
        "P101": {"Category": "Electronics", "Rating": 4.5},
        "P102": {"Category": "Accessories", "Rating": 4.2},
        "P103": {"Category": "Accessories", "Rating": 4.0},
    }

    return mock_api_data.get(product_id, {"Category": "Unknown", "Rating": "N/A"})

