"""Sales Data Analyzer
Reads sales.csv, calculates key business metrics, prints a summary
in the terminal, and saves the same report to sales_report.txt.

Usage:
    python sales_analyzer.py                      # uses sales.csv
    python sales_analyzer.py my_data.csv          # custom input file
    python sales_analyzer.py my_data.csv out.txt  # custom input and output
"""

import csv
import sys
from collections import defaultdict

INPUT_FILE = "sales.csv"
REPORT_FILE = "sales_report.txt"
REQUIRED_COLUMNS = ["order_id", "date", "product", "category", "quantity", "unit_price"]


class DataError(Exception):
    """Raised when the input file cannot be used at all."""


def parse_row(row, line_number):
    """Validate one CSV row and return a clean dictionary.
    Raises ValueError with a readable message if the row is invalid."""
    order_id = (row["order_id"] or "").strip()
    product = (row["product"] or "").strip()
    if not order_id:
        raise ValueError("missing order_id")
    if not product:
        raise ValueError("missing product name")

    try:
        quantity = int((row["quantity"] or "").strip())
    except ValueError:
        raise ValueError(f"quantity '{row['quantity']}' is not a whole number")
    if quantity <= 0:
        raise ValueError(f"quantity must be greater than 0 (got {quantity})")

    try:
        unit_price = float((row["unit_price"] or "").strip())
    except ValueError:
        raise ValueError(f"unit_price '{row['unit_price']}' is not a number")
    if unit_price <= 0 or unit_price != unit_price or unit_price == float("inf"):
        raise ValueError(f"unit_price must be a positive number (got {row['unit_price']})")

    return {
        "order_id": order_id,
        "product": product,
        "quantity": quantity,
        "unit_price": unit_price,
    }


def load_sales(file_path):
    """Read the CSV file and return (valid_records, skipped_rows)."""
    try:
        # utf-8-sig also handles files saved by Excel with a BOM
        with open(file_path, newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames is None:
                raise DataError(f"'{file_path}' is empty.")

            reader.fieldnames = [name.strip() for name in reader.fieldnames]
            missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing:
                raise DataError("Missing required column(s): " + ", ".join(missing))

            records, skipped = [], []
            for line_number, row in enumerate(reader, start=2):  # line 1 = header
                try:
                    records.append(parse_row(row, line_number))
                except ValueError as error:
                    skipped.append((line_number, str(error)))
    except FileNotFoundError:
        raise DataError(f"File not found: '{file_path}'. Place it next to the script.")
    except PermissionError:
        raise DataError(f"No permission to read '{file_path}'.")
    except UnicodeDecodeError:
        raise DataError(f"'{file_path}' is not a valid UTF-8 text/CSV file.")

    if not records:
        raise DataError("No valid sales records were found in the file.")
    return records, skipped


def analyze(records):
    """Calculate all summary metrics from the valid records."""
    revenue_by_product = defaultdict(float)
    quantity_by_product = defaultdict(int)
    unique_orders = set()
    total_revenue = 0.0
    total_quantity = 0

    for record in records:
        line_revenue = record["quantity"] * record["unit_price"]
        total_revenue += line_revenue
        total_quantity += record["quantity"]
        revenue_by_product[record["product"]] += line_revenue
        quantity_by_product[record["product"]] += record["quantity"]
        unique_orders.add(record["order_id"])

    order_count = len(unique_orders)
    # Highest revenue first; product name breaks ties so output is stable
    ranking = sorted(revenue_by_product.items(), key=lambda item: (-item[1], item[0]))

    return {
        "total_revenue": total_revenue,
        "order_count": order_count,
        "total_quantity": total_quantity,
        "average_order_value": total_revenue / order_count,
        "top_product": ranking[0],
        "ranking": ranking,
        "quantity_by_product": quantity_by_product,
    }


def build_report(results, source_file, skipped):
    """Return the report as a single formatted string."""
    line = "=" * 62
    thin = "-" * 62
    top_name, top_revenue = results["top_product"]

    lines = [
        line,
        "SALES DATA ANALYSIS REPORT".center(62),
        line,
        f"Source file          : {source_file}",
        f"Total revenue        : ${results['total_revenue']:,.2f}",
        f"Unique orders        : {results['order_count']}",
        f"Total units sold     : {results['total_quantity']}",
        f"Average order value  : ${results['average_order_value']:,.2f}",
        f"Top product          : {top_name} (${top_revenue:,.2f})",
        thin,
        "REVENUE BY PRODUCT (highest to lowest)",
        thin,
        f"{'#':<3}{'Product':<26}{'Units':>7}{'Revenue':>14}{'Share':>9}",
    ]
    for rank, (product, revenue) in enumerate(results["ranking"], start=1):
        units = results["quantity_by_product"][product]
        share = revenue / results["total_revenue"] * 100
        lines.append(f"{rank:<3}{product:<26}{units:>7}{revenue:>14,.2f}{share:>8.1f}%")

    if skipped:
        lines += [thin, f"WARNINGS: {len(skipped)} row(s) skipped due to invalid data", thin]
        lines += [f"Line {number}: {reason}" for number, reason in skipped]
    lines.append(line)
    return "\n".join(lines)


def save_report(report_text, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report_text + "\n")


def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE
    output_file = sys.argv[2] if len(sys.argv) > 2 else REPORT_FILE
    try:
        records, skipped = load_sales(input_file)
        report = build_report(analyze(records), input_file, skipped)
        print(report)
        save_report(report, output_file)
        print(f"\nReport saved to: {output_file}")
    except DataError as error:
        print(f"Error: {error}")
        sys.exit(1)
    except OSError as error:
        print(f"Error: could not write the report ({error}).")
        sys.exit(1)


if __name__ == "__main__":
    main()
