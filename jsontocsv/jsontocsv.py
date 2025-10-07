import json
import csv
from pathlib import Path

def json_to_csv(json_file, csv_file):
    """
    Convert a JSON file to a CSV file.
    Supports lists of dictionaries and nested objects.
    """

    # Load JSON data
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure data is a list of dicts
    if isinstance(data, dict):
        if "records" in data:
            data = data["records"]
        else:
            data = [data]

    # Flatten nested JSON objects
    def flatten(d, parent_key="", sep="."):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    flat_data = [flatten(item) for item in data]

    # Write to CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted({key for d in flat_data for key in d}))
        writer.writeheader()
        writer.writerows(flat_data)

    print(f"\n✅ Successfully converted '{json_file}' → '{csv_file}'")

def main():
    json_path = input("Enter the path to the JSON file: ").strip()
    csv_path = input("Enter the desired path for the CSV output file: ").strip()

    json_file = Path(json_path)
    csv_file = Path(csv_path)

    if not json_file.exists():
        print(f"❌ Error: '{json_file}' not found.")
        return

    json_to_csv(json_file, csv_file)

if __name__ == "__main__":
    main()
