def read_sales_file(file_path):
    records = []

    try:
        with open(file_path, 'r', encoding='latin-1') as file:
            for line in file:
                line = line.strip()
                if line:
                    records.append(line)
    except Exception as e:
        print("Error reading file:", e)

    return records
