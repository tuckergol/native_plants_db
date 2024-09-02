from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize the plant database and the log database
def init_db():
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        # Initialize the plant database
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY,
            common_name TEXT,
            botanical_name TEXT
        )
        ''')
        
        # Initialize the log database
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            common_name TEXT,
            botanical_name TEXT,
            locations TEXT
        )
        ''')

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    search_results = []
    if request.method == 'POST':
        # Handle search
        common_name = request.form.get('common_name')
        with sqlite3.connect('native_plants.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plants WHERE common_name LIKE ?", ('%' + common_name + '%',))
            search_results = cursor.fetchall()
    return render_template('index.html', search_results=search_results)

@app.route('/log', methods=['POST'])
def log_plant():
    common_name = request.form.get('common_name')
    botanical_name = request.form.get('botanical_name')  # Retrieve botanical name
    locations = request.form.getlist('locations')
    locations_str = ', '.join(locations)
    
    # Insert into logs database
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (common_name, botanical_name, locations) VALUES (?, ?, ?)", 
                       (common_name, botanical_name, locations_str))
        conn.commit()
    
    return redirect(url_for('index'))

@app.route('/view_logs')
def view_logs():
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs")
        log_data = cursor.fetchall()
    return render_template('view_logs.html', log_data=log_data)

if __name__ == '__main__':
    app.run(debug=True)
