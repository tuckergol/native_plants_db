import pandas as pd
from sqlalchemy import create_engine

# Load CSV file
df = pd.read_csv('filtered_native_plants.csv')

# Display first few rows
print(df.head())

# Set up database engine
engine = create_engine('sqlite:///native_plants.db')

# Save DataFrame to database
df.to_sql('plants', con=engine, if_exists='replace', index=False)
