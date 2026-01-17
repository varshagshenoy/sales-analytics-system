from pathlib import Path

# function to read sales data with encoding handling
def read_sales_data(filename):
    current_path = Path(__file__)
    base_path = current_path.parent.parent
    data_path = base_path/"data"/filename

    # handle FileNotFoundError
    if not data_path.exists():
        print(f"Error: The file {filename} was not found.")
        return []

    # try different encodings - file will be read with the first one that succeeds
    encodings_list = ['utf-8','latin-1','cp1252']

    for enc in encodings_list:
        try:
            data_list = []
            with open(data_path, "r", encoding=enc) as f:
                # 'next' returns the next item from an iterator. A file opened with 'open' (here, 'f') is an iterator
                # this line reads and skips the header row, file pointer moves to the second line - the loop below starts from the second line
                # returns None if file is empty
                next(f, None)
                
                for line in f:
                    # skip the empty lines
                    # strip removes leading/trailing spaces and newline characters
                    # If a line only contained these, strip() returns an empty string "" - empty string evaluates to false
                    cleaned_line = line.strip()
                    if cleaned_line:
                        data_list.append(cleaned_line)

            # returns a list of raw lines (strings)
            return data_list
        
        # handle encoding issues
        except UnicodeDecodeError:
            print(f"Error: Failed to read file with: {enc}.")
            continue
    return []


# function to parse raw data and handle data quality issues
def parse_transactions(raw_lines):
    keys = ['TransactionID', 'Date', 'ProductID', 'ProductName','Quantity', 'UnitPrice', 'CustomerID', 'Region']
    clean_data_list = []

    for raw_line in raw_lines:
        values = raw_line.split('|')

        # skip rows with incorrect number of fields
        if len(values) != len(keys):
            continue

        # map keys to values to form a dictionary for a transaction record
        record = dict(zip(keys,values))

        # handle commas within ProductName - replace with space
        record['ProductName'] = record['ProductName'].replace(',', ' ').strip()

        try:
            # Quantity -> Remove commas and convert to int
            record['Quantity'] = int(record['Quantity'].replace(',','').strip())

            # UnitPrice -> Remove commas and convert to float
            record['UnitPrice'] = float(record['UnitPrice'].replace(',','').strip())
        except ValueError:
            continue

        clean_data_list.append(record)

    # returns a clean list of dictionaries 
    return clean_data_list


# function to validate and filter transactions
def validate_and_filter(transactions, region=None, min_amount=None, max_amount=None):
    valid_transactions = []
    invalid_count = 0
    required_fields = ['TransactionID', 'Date', 'ProductID', 'ProductName', 'Quantity', 'UnitPrice', 'CustomerID', 'Region']

    # ------ VALIDATION ------
    
    for record in transactions:
        # validates if all required fields are present
        if any(record[field] == '' for field in required_fields):
            invalid_count += 1
            continue

        # validates if quantity and unit price values are greater than 0
        if record['Quantity'] <= 0 or record['UnitPrice'] <= 0:
            invalid_count += 1
            continue

        # validates if TransactionID starts with 'T', ProductID starts with 'P' and CustomerID starts with 'C'
        if not (record['TransactionID'].startswith('T') and record['ProductID'].startswith('P') and record['CustomerID'].startswith('C')):
            invalid_count += 1
            continue

        valid_transactions.append(record)

    # ------ FILTER DISPLAY ------
    
    # display available regions
    regions_list = sorted(set(record['Region'] for record in valid_transactions if record['Region']))
    print(f"Available regions: {regions_list}")

    # display transaction amount range (min/max)
    amounts = [record['Quantity'] * record['UnitPrice'] for record in valid_transactions]
    if amounts:
        print(f"Transaction amount range: {min(amounts)} to {max(amounts)}")

    # ------ FILTERING ------

    filtered_by_region = 0
    filtered_by_amount = 0
    filtered = valid_transactions
    
    # filtering by region
    if region:
        before = len(filtered)
        region_normalized = region.strip().lower()
        filtered = [record for record in filtered if record['Region'].strip().lower() == region_normalized]
        filtered_by_region = before - len(filtered)
        print(f"Count of records after applying region filter ({region}): {len(filtered)}")

    # filtering by minimum transaction amount
    if min_amount is not None:
        before = len(filtered)
        filtered = [record for record in filtered if record['Quantity'] * record['UnitPrice'] >= float(min_amount)]
        filtered_by_amount += before - len(filtered)
        print(f"Count of records after applying min amount filter ({min_amount}): {len(filtered)}")

    # filtering by maximum transaction amount
    if max_amount is not None:
        before = len(filtered)
        filtered = [record for record in filtered if record['Quantity'] * record['UnitPrice'] <= float(max_amount)]
        filtered_by_amount += before - len(filtered)
        print(f"Count of records after applying max amount filter ({max_amount}): {len(filtered)}")

    # ------ SUMMARY ------

    filter_summary = {
        'total_input': len(transactions),
        'invalid': invalid_count,
        'filtered_by_region': filtered_by_region,
        'filtered_by_amount': filtered_by_amount,
        'final_count': len(filtered)
    }

    # returns a tuple containing a list of valid filtered transactions (dictionaries), count of invalid transactions and a filter summary dictionary
    return (filtered, invalid_count, filter_summary)
