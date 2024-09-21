from flask import Flask, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize plant database and log database
def init_db():
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY,
            common_name TEXT,
            botanical_name TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            common_name TEXT,
            locations TEXT,
            status TEXT,
            time TEXT
        )
        ''')
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    search_results = []
    if request.method == 'POST':
        common_name = request.form.get('common_name')
        with sqlite3.connect('native_plants.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM plants WHERE common_name LIKE ?", ('%' + common_name + '%',))
            search_results = cursor.fetchall()
    return render_template('index.html', search_results=search_results)

@app.route('/log_plant', methods=['GET'])
def log_plant_page():
    common_name = request.args.get('common_name')
    return render_template('log_plant.html', common_name=common_name)

@app.route('/log', methods=['POST'])
def log_plant():
    common_name = request.form.get('common_name')
    location = request.form.get('locations')
    status = request.form.get('status')
    week = request.form.get('week')
    year = request.form.get('year')
    
    # Combine year and week for 'time' column
    time_log = f"{year}, Week {week}"
    
    # Insert into logs database
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (common_name, locations, status, time) VALUES (?, ?, ?, ?)",
                       (common_name, location, status, time_log))
        conn.commit()
    
    return redirect(url_for('index'))

# View plant logs
@app.route('/view_logs')
def view_logs():
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs")
        log_data = cursor.fetchall()
    return render_template('view_logs.html', log_data=log_data)

if __name__ == '__main__':
    app.run(debug=True)
