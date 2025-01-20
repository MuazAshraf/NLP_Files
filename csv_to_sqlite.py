import sqlite3
import pandas as pd
import os

# Step 1: Read CSV file into DataFrame
csv_file = 'medical\healthcare_dataset.csv'  # Replace with the path to your CSV file
df = pd.read_csv(csv_file)

# Step 2: Automatically generate a table name from the CSV filename (remove extension)
table_name = os.path.splitext(os.path.basename(csv_file))[0] 

# Step 2: Connect to SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('healthcare.db')  # Replace with your desired SQLite DB name

# Step 3: Write DataFrame to SQLite (replace or append data)
df.to_sql(table_name, conn, if_exists='replace', index=False)  # Use 'replace' to overwrite or 'append' to add rows

# Step 4: Close the connection
conn.close()

print("CSV successfully converted to SQLite database!")
