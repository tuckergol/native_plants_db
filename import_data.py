import pandas as pd
from sqlalchemy import create_engine

# Load the CSV file
df = pd.read_csv('filtered_native_plants.csv')

# Display the first few rows
print(df.head())

# Set up the database engine
engine = create_engine('sqlite:///native_plants.db')

# Save the DataFrame to the database
df.to_sql('plants', con=engine, if_exists='replace', index=False)
