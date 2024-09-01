from flask import Flask, render_template
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)
engine = create_engine('sqlite:///native_plants.db')

@app.route('/')
def index():
    df = pd.read_sql('plants', con=engine)
    return render_template('index.html', tables=[df.to_html(classes='data')], titles=df.columns.values)

if __name__ == '__main__':
    app.run(debug=True)
