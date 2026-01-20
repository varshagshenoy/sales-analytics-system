import requests
import csv
from pathlib import Path

# function to fetch all products from DummyJSON API
def fetch_all_products():
    url = 'https://dummyjson.com/products?limit=100'

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad status codes (4xx or 5xx)

        data = response.json()
        products = data.get('products', [])

        print(f"Successfully fetched {len(products)} products from API")
        # returns list of product dictionaries
        return products
    
    except requests.exceptions.RequestException as err:
        # Handles any errors that occurred during the request
        print(f"Failed to fetch products from API: {err}")
        # returns empty list if API fails
        return []


# function to create a mapping of product IDs to product info
def create_product_mapping(api_products):
    product_mapping = {}

    for product in api_products:
        product_mapping[product['id']] = {
            'title': product.get('title', ''),
            'category': product.get('category', ''),
            'brand': product.get('brand', 'Unknown'),
            'rating': product.get('rating', 0.0)
        }

    # returns dictionary with mapping
    return product_mapping


# function to enrich transaction data with API product information
def enrich_sales_data(transactions, product_mapping):
    enriched_transactions = []

    for record in transactions:
        # Creates a copy so original data is not mutated
        enriched_record = record.copy()

        # default values
        enriched_record['API_Category'] = None
        enriched_record['API_Brand'] = None
        enriched_record['API_Rating'] = None
        enriched_record['API_Match'] = False

        try:
            # Extract numeric product ID (e.g., P101 -> 101)
            productID = record['ProductID']
            num_productID = int(productID[1:])
        except (KeyError, ValueError, TypeError):
            # If ProductID is missing or malformed
            enriched_transactions.append(enriched_record)
            continue

        # Check if product exists in API mapping and add API fields
        if num_productID in product_mapping:
            api_info = product_mapping.get(num_productID)

            enriched_record['API_Category'] = api_info.get('category')
            enriched_record['API_Brand'] = api_info.get('brand')
            enriched_record['API_Rating'] = api_info.get('rating')
            enriched_record['API_Match'] = True

        enriched_transactions.append(enriched_record)

    # returns list of enriched transaction dictionaries
    return enriched_transactions


# function to save enriched transactions back to file
def save_enriched_data(enriched_transactions, filename='data/enriched_sales_data.txt'):
    base = Path(__file__).parent.parent
    data_path = base / filename

    column_headers = ['TransactionID', 'Date', 'ProductID', 'ProductName', 'Quantity', 'UnitPrice', 'CustomerID', 'Region', 'API_Category', 'API_Brand', 'API_Rating', 'API_Match']

    with open(data_path, 'w', encoding='utf-8', newline='') as f:

        # Create a DictWriter object with the file, fieldnames, and pipe delimiter
        writer = csv.DictWriter(f, fieldnames=column_headers, delimiter='|')

        # Write the header row
        writer.writeheader()

        # Write all the rows of data
        # csv.DictWriter automatically serializes None values as empty fields in the pipe-delimited output
        writer.writerows(enriched_transactions)
            