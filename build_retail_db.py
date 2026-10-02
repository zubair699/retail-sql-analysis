

import pandas as pd
import sqlite3


# STEP 1: Load the raw CSV

df = pd.read_csv("Online_Retail.csv", encoding="ISO-8859-1")
df.columns = ["InvoiceNo", "StockCode", "Description", "Quantity",
              "InvoiceDate", "UnitPrice", "CustomerID", "Country"]
print("Raw rows:", len(df))

# STEP 2: Clean the data

# Drop exact duplicate rows
df = df.drop_duplicates()

# Drop junk "adjust bad debt" accounting rows (negative price, not real sales)
df = df[df["UnitPrice"] >= 0]

# Drop rows with no CustomerID (we only want identified customers)
df = df.dropna(subset=["CustomerID"])
df["CustomerID"] = df["CustomerID"].astype(int)

# Fill missing product descriptions
df["Description"] = df["Description"].fillna("UNKNOWN ITEM").str.strip()

# Parse the date column properly
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="%m/%d/%y %H:%M")


# STEP 3: Split into sales vs returns
# InvoiceNo starting with "C" = cancelled/returned order (negative quantity)

sales = df[df["Quantity"] > 0].copy()
returns = df[df["Quantity"] < 0].copy()
returns["Quantity"] = returns["Quantity"].abs()

print("Sales rows:", len(sales))
print("Returns rows:", len(returns))


# STEP 4: Build normalized tables (this is the schema design step)


# customers: one row per unique customer
customers = (
    sales.groupby("CustomerID")
    .agg(country=("Country", "first"))
    .reset_index()
    .rename(columns={"CustomerID": "customer_id"})
)

# products: one row per unique product, using the most common price seen
products = (
    sales.groupby("StockCode")
    .agg(
        description=("Description", "first"),
        unit_price=("UnitPrice", lambda x: x.mode()[0] if not x.mode().empty else x.iloc[0]),
    )
    .reset_index()
    .rename(columns={"StockCode": "product_id"})
)

# orders: one row per invoice
orders = (
    sales.groupby("InvoiceNo")
    .agg(customer_id=("CustomerID", "first"), order_date=("InvoiceDate", "first"))
    .reset_index()
    .rename(columns={"InvoiceNo": "order_id"})
)

# order_items: one row per line item (the fact table)
order_items = sales[["InvoiceNo", "StockCode", "Quantity", "UnitPrice"]].copy()
order_items.columns = ["order_id", "product_id", "quantity", "unit_price"]
order_items.insert(0, "order_item_id", range(1, len(order_items) + 1))

# returns: kept as its own table for separate analysis
returns_tbl = returns[["InvoiceNo", "StockCode", "CustomerID", "Quantity", "UnitPrice", "InvoiceDate"]].copy()
returns_tbl.columns = ["return_invoice_id", "product_id", "customer_id", "quantity", "unit_price", "return_date"]
returns_tbl.insert(0, "return_id", range(1, len(returns_tbl) + 1))


# STEP 5: Write everything into a SQLite database file

conn = sqlite3.connect("retail.db")
customers.to_sql("customers", conn, if_exists="replace", index=False)
products.to_sql("products", conn, if_exists="replace", index=False)
orders.to_sql("orders", conn, if_exists="replace", index=False)
order_items.to_sql("order_items", conn, if_exists="replace", index=False)
returns_tbl.to_sql("returns", conn, if_exists="replace", index=False)
conn.close()

print("Done! retail.db created with 5 tables.")