import pandas as pd
import glob

files = glob.glob("data/daily_sales_data_*.csv")
df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

pink = df[df['product'].str.contains("Pink Morsel", case=False, na=False)].copy()

pink['price'] = pd.to_numeric(pink['price'].replace(r'[\$,]', '', regex=True), errors='coerce')
pink['quantity'] = pd.to_numeric(pink['quantity'], errors='coerce')

pink['Sales'] = pink['price'] * pink['quantity']


output = pink[['Sales', 'date', 'region']].rename(columns={'date': 'Date', 'region': 'Region'})

output.to_csv("formatted_sales_data.csv", index=False)

print("Formatted file created: formatted_sales_data.csv")
