# --------------- SALES SUMMARY CALCULATOR ---------------

# ------ Calculate Total Revenue ------

# Calculates total revenue from all transactions
def calculate_total_revenue(transactions):
    # Total revenue will be a float value
    total_revenue = 0.0

    for record in transactions:
        total_revenue += record['Quantity'] * record['UnitPrice']
    
    return round(total_revenue, 2)

# ------ Region-wise Sales Analysis ------

# Analyzes sales by region
def region_wise_sales(transactions):
    region_stats = {}
    grand_total = 0.0

    # Calculates total sales and transaction count per region
    for record in transactions:
        region = record['Region']
        amount = record['Quantity'] * record['UnitPrice']

        grand_total += amount

        if region not in region_stats:
            region_stats[region] = {
                'total_sales': 0.0,
                'transaction_count': 0,
            }

        region_stats[region]['total_sales'] += amount
        region_stats[region]['transaction_count'] += 1

    # Calculates percentage of total sales
    for region in region_stats.values():
        percentage = (region['total_sales']/grand_total) * 100 if grand_total > 0 else 0.0
        region['percentage'] = round(percentage, 2)
        region['total_sales'] = round(region['total_sales'], 2)

    # Sorts by total_sales in descending order
    items = region_stats.items()
    sorted_items = sorted(items, key=lambda item: item[1]['total_sales'], reverse=True)
    sorted_region_stats = dict(sorted_items)

    # Returns dictionary with region statistics
    return sorted_region_stats

# ------ Top Selling Products ------

# Finds top n products by total quantity sold
def top_selling_products(transactions, n=5):
    product_stats = {}

    # Calculates total quantity sold and total revenue for each product
    for record in transactions:
        product = record['ProductName']
        quantity = record['Quantity']
        amount = quantity * record['UnitPrice']

        if product not in product_stats:
            product_stats[product] = {
                'total_quantity': 0,
                'total_revenue': 0.0,
            }

        product_stats[product]['total_quantity'] += quantity
        product_stats[product]['total_revenue'] += amount

    products_list = [(product,stats['total_quantity'],round(stats['total_revenue'], 2)) for product, stats in product_stats.items()]

    # Sorts by total_quantity in descending order
    sorted_products = sorted(products_list, key=lambda item: item[1], reverse=True)
    top_sorted_products = sorted_products[:n]
    
    # Returns top n products (list of tuples)
    return top_sorted_products

# ------ Customer Purchase Analysis ------

# Analyzes customer purchase patterns
def customer_analysis(transactions):
    customer_stats = {}

    # Calculates total amount spent and total count of purchases per customer
    # Creates list of unique products bought per customer
    for record in transactions:
        customer = record['CustomerID']
        amount = record['Quantity'] * record['UnitPrice']
        product = record['ProductName']

        if customer not in customer_stats:
            customer_stats[customer] = {
                'total_spent': 0.0,
                'purchase_count': 0,
                'products_bought': set()
            }

        customer_stats[customer]['total_spent'] += amount
        customer_stats[customer]['purchase_count'] += 1
        customer_stats[customer]['products_bought'].add(product)

    # Calculates average order value
    for customer in customer_stats.values():
        average_order_value = customer['total_spent']/customer['purchase_count']
        customer['avg_order_value'] = round(average_order_value,2)
        customer['total_spent'] = round(customer['total_spent'], 2)
        customer['products_bought'] = sorted(customer['products_bought'])

    # Sorts by total_spent in descending order
    items = customer_stats.items()
    sorted_items = sorted(items, key=lambda item: item[1]['total_spent'], reverse=True)
    sorted_customer_stats = dict(sorted_items)

    # Returns dictionary of customer statistics
    return sorted_customer_stats
    

# --------------- DATE-BASED ANALYSIS ---------------

# ------ Daily Sales Trend ------

# Analyzes sales trend by date
def daily_sales_trend(transactions):
    date_stats = {}

    # Calculates daily revenue and count of daily transactions
    for record in transactions:
        date = record['Date']
        amount = record['Quantity'] * record['UnitPrice']
        customer = record['CustomerID']

        if date not in date_stats:
            date_stats[date] = {
                'revenue': 0.0,
                'transaction_count': 0,
                'customers': set()
            }
        
        date_stats[date]['revenue'] += amount
        date_stats[date]['transaction_count'] += 1
        date_stats[date]['customers'].add(customer)

    # Counts unique customers per day - converts customer set to counts
    for stats in date_stats.values():
        stats['unique_customers'] = len(stats['customers'])
        del stats['customers']

    # Sorts chronologically
    sorted_date_stats = dict(sorted(date_stats.items()))
    
    # Returns dictionary of daily sales statistics, sorted by date
    return sorted_date_stats

# ------ Find Peak Sales Day ------

# Identifies the date with highest revenue
def find_peak_sales_day(transactions):
    date_stats = {}

    # Aggregates revenue and transaction count per date
    for record in transactions:
        date = record['Date']
        amount = record['Quantity'] * record['UnitPrice']

        if date not in date_stats:
            date_stats[date] = {
                'revenue': 0.0,
                'transaction_count': 0,
            }

        date_stats[date]['revenue'] += amount
        date_stats[date]['transaction_count'] += 1

    # Find peak sales day
    items = date_stats.items()
    peak_date, stats = max(items, key=lambda item: item[1]['revenue'])
    
    # returns a tuple for date with highest revenue
    return (peak_date, stats['revenue'], stats['transaction_count'])


# --------------- PRODUCT PERFORMANCE ---------------

# ------ Low Performing Products ------

# Identifies products with low sales
def low_performing_products(transactions, threshold=10):
    product_stats = {}

    # Calculates total quantity sold and total revenue for each product
    for record in transactions:
        product = record['ProductName']
        quantity = record['Quantity']
        amount = quantity * record['UnitPrice']

        if product not in product_stats:
            product_stats[product] = {
                'total_quantity': 0,
                'total_revenue': 0.0,
            }

        product_stats[product]['total_quantity'] += quantity
        product_stats[product]['total_revenue'] += amount

    # Filter low-performing products - products with total quantity < threshold
    low_performers = []

    for product, stats in product_stats.items():
        if stats['total_quantity'] < threshold:
            low_performers.append((product, stats['total_quantity'], stats['total_revenue']))

    # Sorts by total_quantity in ascending order
    low_performers.sort(key=lambda item: item[1])
    
    # Returns products with low sales (list of tuples)
    return low_performers