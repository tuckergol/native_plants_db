from flask import Flask, request, render_template, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = '5879525e56541bdc293ebc85669f138233abde93e8399bd5'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User class
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return User(id=user[0], username=user[1], password=user[2])
    return None

# Initialize plant, user, and location databases
def init_db():
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
        ''')
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
            user_id INTEGER,
            common_name TEXT,
            locations TEXT,
            status TEXT,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            location_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        with sqlite3.connect('native_plants.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'danger')
                return redirect(url_for('signup'))
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect('native_plants.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if user and bcrypt.check_password_hash(user[2], password):
                user_obj = User(id=user[0], username=user[1], password=user[2])
                login_user(user_obj)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/log_plant', methods=['GET'])
@login_required
def log_plant_page():
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM locations WHERE user_id = ?", (current_user.id,))
        locations = cursor.fetchall()
    return render_template('log_plant.html', common_name=request.args.get('common_name'), locations=locations)

@app.route('/log', methods=['POST'])
@login_required
def log_plant():
    common_name = request.form.get('common_name')
    selected_location = request.form.get('locations')
    custom_location = request.form.get('custom_location')
    location = selected_location if selected_location else custom_location
    status = request.form.get('status')

    month = request.form.get('month').zfill(2)
    day = request.form.get('day').zfill(2)
    year = request.form.get('year')
    date = f"{month}/{day}/{year}"
    
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO logs (user_id, common_name, locations, status, date) VALUES (?, ?, ?, ?, ?)",
                       (current_user.id, common_name, location, status, date))
        conn.commit()
    
    return redirect(url_for('index'))

@app.route('/manage_locations', methods=['GET', 'POST'])
@login_required
def manage_locations():
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            location_name = request.form.get('location_name')
            cursor.execute("INSERT INTO locations (user_id, location_name) VALUES (?, ?)",
                           (current_user.id, location_name))
            conn.commit()
            flash('Location added successfully!', 'success')

        cursor.execute("SELECT * FROM locations WHERE user_id = ?", (current_user.id,))
        locations = cursor.fetchall()
    return render_template('manage_locations.html', locations=locations)

@app.route('/delete_location/<int:location_id>', methods=['POST'])
@login_required
def delete_location(location_id):
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM locations WHERE id = ? AND user_id = ?", (location_id, current_user.id))
        conn.commit()
    flash('Location deleted successfully!', 'success')
    return redirect(url_for('manage_locations'))

@app.route('/view_logs')
@login_required
def view_logs():
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs WHERE user_id = ?", (current_user.id,))
        log_data = cursor.fetchall()
    return render_template('view_logs.html', log_data=log_data)

@app.route('/delete_log/<int:log_id>', methods=['POST'])
@login_required
def delete_log(log_id):
    with sqlite3.connect('native_plants.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM logs WHERE id = ? AND user_id = ?", (log_id, current_user.id))
        conn.commit()
    flash('Log deleted successfully!', 'success')
    return redirect(url_for('view_logs'))

if __name__ == '__main__':
    app.run(debug=True)
