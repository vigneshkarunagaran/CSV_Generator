import csv
import random
import string
from datetime import datetime, timedelta

def generate_random_string(length=8):
    """
    Generate a random alphanumeric string of given length.
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_date(start_year=2000, end_year=2025):
    """
    Generate a random date string between start_year and end_year.
    Format: YYYY-MM-DD
    """
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

def generate_column_data(col_def, num_rows):
    """
    Generate a list of data for a single column based on its definition.
    
    Parameters:
        col_def (dict): Column definition including 'name', 'type', and 'allow_duplicates'.
        num_rows (int): Number of rows to generate.

    Returns:
        List: Generated column data.
    """
    values = set()
    data = []

    # Case 1: Fixed list of possible values
    if isinstance(col_def['type'], list):
        options = col_def['type']
        if not col_def.get("allow_duplicates", True) and len(options) < num_rows:
            raise ValueError(f"Cannot generate {num_rows} unique values from {options}")
        while len(data) < num_rows:
            value = random.choice(options)
            if col_def.get("allow_duplicates", True) or value not in values:
                data.append(value)
                values.add(value)
        return data

    # Case 2: Generated from type
    datatype = col_def['type']
    allow_duplicates = col_def.get("allow_duplicates", True)

    while len(data) < num_rows:
        if datatype == "int":
            value = random.randint(1, 10000)
        elif datatype == "float":
            value = round(random.uniform(1.0, 10000.0), 2)
        elif datatype == "str":
            value = generate_random_string()
        elif datatype == "date":
            value = generate_random_date()
        else:
            raise ValueError(f"Unsupported datatype: {datatype}")

        if allow_duplicates or value not in values:
            data.append(value)
            values.add(value)

    return data

def generate_csv(schema, num_rows, output_file):
    """
    Generate a CSV file with random data based on schema.

    Parameters:
        schema (List[Dict]): List of column definitions.
        num_rows (int): Number of rows to generate.
        output_file (str): Output CSV file path.
    """
    column_data = {}

    for col in schema:
        column_data[col["name"]] = generate_column_data(col, num_rows)

    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([col["name"] for col in schema])
        for i in range(num_rows):
            writer.writerow([column_data[col["name"]][i] for col in schema])

# Example usage
if __name__ == "__main__":
    schema = [
        {"name": "id", "type": "int", "allow_duplicates": False},
        {"name": "name", "type": ["Alice", "Bob", "Charlie"], "allow_duplicates": True},
        {"name": "score", "type": "float", "allow_duplicates": True},
        {"name": "dob", "type": "date", "allow_duplicates": True},
    ]

    generate_csv(schema, num_rows=100, output_file="output.csv")