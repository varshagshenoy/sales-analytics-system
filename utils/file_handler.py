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