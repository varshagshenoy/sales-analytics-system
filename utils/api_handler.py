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

