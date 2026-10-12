# Sales Data Analyzer

A small Python command-line tool that reads sales records from a CSV file, calculates key business metrics, and produces a clear summary report in the terminal and as a text file.

It uses only Python's standard library. No installation, paid services, or external packages are needed.

## What it calculates

- Total revenue (`quantity × unit_price` for every row)
- Number of unique orders (an order can contain several product rows)
- Total units sold
- Average order value (total revenue ÷ unique orders, not ÷ CSV rows)
- Top product by revenue
- Revenue, units, and share of total for every product, sorted highest to lowest

## Requirements

- Python 3.9 or newer

## Usage

1. Put `sales_analyzer.py` and `sales.csv` in the same folder.
2. Open a terminal in that folder and run:

```bash
python sales_analyzer.py
```

(On some systems use `python3` instead of `python`.)

The summary prints in the terminal and is saved to `sales_report.txt`.

To use your own files:

```bash
python sales_analyzer.py my_data.csv my_report.txt
```

## Input format

The CSV must have a header row with these columns (extra columns are ignored):

| Column       | Description                       |
|--------------|-----------------------------------|
| `order_id`   | Order identifier (text or number) |
| `date`       | Order date                        |
| `product`    | Product name                      |
| `category`   | Product category                  |
| `quantity`   | Whole number greater than 0       |
| `unit_price` | Number greater than 0             |

`sales.csv` contains 14 rows of fictional sample data (11 orders, 7 products).

## Error handling

| Situation                         | Behavior                                                      |
|-----------------------------------|---------------------------------------------------------------|
| File not found                    | Clear error message, exit code 1                              |
| Missing required column           | Lists the missing column(s), exit code 1                      |
| Empty file or no valid rows       | Clear error message, exit code 1                              |
| Invalid quantity / price / blank order ID | That row is skipped and listed under WARNINGS in the report |

## Project structure

```
sales_analyzer.py   Main program
sales.csv           Sample dataset (fictional)
sales_report.txt    Report generated from the sample dataset
README.md           This file
```

## Limitations

- Revenue is calculated with standard floating-point numbers and rounded to 2 decimals for display. This is fine for reporting but not meant for accounting-grade precision.
- The `date` and `category` columns are required but not yet used in the calculations. They are natural next steps (monthly or category breakdowns).
