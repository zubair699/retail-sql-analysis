

import pandas as pd
import sqlite3


QUERY = """
SELECT p.description, SUM(oi.quantity) AS total_units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY total_units_sold DESC
LIMIT 10;
"""


conn = sqlite3.connect("retail.db")
result = pd.read_sql(QUERY, conn)
conn.close()

print(result.to_string(index=False))
print()
print(f"({len(result)} rows returned)")