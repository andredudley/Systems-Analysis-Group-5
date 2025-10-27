from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sky_acres_farm_secret_key_2024_change_in_production'

# MySQL Configuration for PythonAnywhere
app.config['MYSQL_HOST'] = 'yourusername.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'yourusername'
app.config['MYSQL_PASSWORD'] = 'your_database_password'
app.config['MYSQL_DB'] = 'yourusername$sky_acres_farm'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def get_db_connection():
    """Get database connection"""
    return mysql.connection

def init_db():
    """Initialize database with all tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Users table for authentication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'manager', 'worker') DEFAULT 'worker',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Employees table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Employees (
                emp_id INT AUTO_INCREMENT PRIMARY KEY,
                FName VARCHAR(50) NOT NULL,
                LName VARCHAR(50) NOT NULL,
                position VARCHAR(100) NOT NULL,
                hire_date DATE NOT NULL,
                phone VARCHAR(20),
                email VARCHAR(100) UNIQUE,
                user_id INT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Vegetation table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Vegetation (
                vi_id INT AUTO_INCREMENT PRIMARY KEY,
                field_location VARCHAR(100) NOT NULL,
                measure_date DATE NOT NULL,
                ndvi_value DECIMAL(5,3) NOT NULL,
                crop_health ENUM('Poor', 'Fair', 'Good', 'Excellent'),
                notes TEXT
            )
        ''')
        
        # Soil table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Soil (
                analysis_id INT AUTO_INCREMENT PRIMARY KEY,
                field_location VARCHAR(100) NOT NULL,
                test_name VARCHAR(100) NOT NULL,
                ph_level DECIMAL(3,1) NOT NULL,
                nitrogen DECIMAL(6,2),
                phosphorus DECIMAL(6,2),
                potassium DECIMAL(6,2)
            )
        ''')
        
        # Storage table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Storage (
                storage_id INT AUTO_INCREMENT PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                quantity DECIMAL(10,2) NOT NULL,
                unit VARCHAR(20) NOT NULL,
                storage_location VARCHAR(100) NOT NULL,
                entry_date DATE NOT NULL,
                condition ENUM('Fresh', 'Good', 'Average', 'Poor')
            )
        ''')
        
        # Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales (
                sale_id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                product VARCHAR(100) NOT NULL,
                quantity DECIMAL(10,2) NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                total_amt DECIMAL(12,2) NOT NULL,
                sale_date DATE NOT NULL,
                payment_status ENUM('Pending', 'Paid', 'Overdue') DEFAULT 'Pending'
            )
        ''')
        
        # Crops table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Crops (
                crop_id INT AUTO_INCREMENT PRIMARY KEY,
                crop_name VARCHAR(100) NOT NULL,
                variety VARCHAR(100) NOT NULL,
                plant_date DATE NOT NULL,
                expected_harvest DATE NOT NULL,
                field_location VARCHAR(100) NOT NULL,
                area_planted DECIMAL(10,2) NOT NULL,
                status ENUM('Planted', 'Growing', 'Harvesting', 'Harvested', 'Failed'),
                notes TEXT,
                created_by INT,
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        ''')
        
        # Livestock table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Livestock (
                animal_id INT AUTO_INCREMENT PRIMARY KEY,
                species VARCHAR(50) NOT NULL,
                breed VARCHAR(50) NOT NULL,
                tag_number VARCHAR(50) UNIQUE NOT NULL,
                birth_date DATE,
                weight DECIMAL(8,2),
                health_status ENUM('Excellent', 'Good', 'Fair', 'Poor', 'Critical'),
                location VARCHAR(100) NOT NULL
            )
        ''')
        
        # Equipment table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Equipment (
                equip_id INT AUTO_INCREMENT PRIMARY KEY,
                equip_name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                purchase_date DATE NOT NULL,
                last_maintenance DATE,
                status ENUM('Operational', 'Maintenance', 'Repair', 'Retired'),
                location VARCHAR(100) NOT NULL
            )
        ''')
        
        # Weather table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Weather (
                weather_id INT AUTO_INCREMENT PRIMARY KEY,
                record_date DATE UNIQUE NOT NULL,
                temp_low DECIMAL(4,1),
                temp_high DECIMAL(4,1),
                rainfall DECIMAL(5,1),
                humidity DECIMAL(4,1),
                wind_speed DECIMAL(5,2)
            )
        ''')
        
        # Marketing Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS MarketingCampaigns (
                campaign_id INT AUTO_INCREMENT PRIMARY KEY,
                campaign_name VARCHAR(100) NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                budget DECIMAL(12,2) NOT NULL,
                target_audience TEXT NOT NULL,
                status ENUM('Planning', 'Active', 'Completed', 'Cancelled')
            )
        ''')
        
        # Transportation table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Transportation (
                transport_id INT AUTO_INCREMENT PRIMARY KEY,
                vehicle_id VARCHAR(50) NOT NULL,
                driver_name VARCHAR(100) NOT NULL,
                route TEXT NOT NULL,
                depart_date DATETIME NOT NULL,
                arrive_date DATETIME,
                cargo_details TEXT NOT NULL,
                status ENUM('Scheduled', 'In Transit', 'Delivered', 'Delayed', 'Cancelled')
            )
        ''')
        
        # Yield table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Yield (
                estimate_id INT AUTO_INCREMENT PRIMARY KEY,
                crop_id INT NOT NULL,
                estimated_yield DECIMAL(10,2) NOT NULL,
                estimated_date DATE NOT NULL,
                actual_yield DECIMAL(10,2),
                variance DECIMAL(10,2),
                FOREIGN KEY (crop_id) REFERENCES Crops(crop_id)
            )
        ''')
        
        conn.commit()
        print("All tables created successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")

# Authentication Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'worker')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)',
                (username, email, password_hash, role)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error creating account. Username or email may already exist.', 'error')
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Main Dashboard
@app.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get counts for dashboard
    cursor.execute('SELECT COUNT(*) as count FROM Employees')
    employee_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM Crops WHERE status != "Harvested"')
    active_crops_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM Livestock')
    livestock_count = cursor.fetchone()['count']
    
    cursor.execute('SELECT SUM(total_amt) as total FROM Sales WHERE sale_date = CURDATE()')
    daily_sales = cursor.fetchone()['total'] or 0
    
    return render_template('dashboard.html', 
                         employee_count=employee_count,
                         active_crops_count=active_crops_count,
                         livestock_count=livestock_count,
                         daily_sales=daily_sales)

# Employee Management
@app.route('/employees')
def employees():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Employees')
    employees = cursor.fetchall()
    return render_template('employees.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        position = request.form['position']
        hire_date = request.form['hire_date']
        phone = request.form['phone']
        email = request.form['email']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Employees (FName, LName, position, hire_date, phone, email) VALUES (%s, %s, %s, %s, %s, %s)',
            (fname, lname, position, hire_date, phone, email)
        )
        conn.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('employees'))
    
    return render_template('add_employee.html')

# Crop Management
@app.route('/crops')
def crops():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, u.username as created_by_name 
        FROM Crops c 
        LEFT JOIN users u ON c.created_by = u.user_id
    ''')
    crops = cursor.fetchall()
    return render_template('crops.html', crops=crops)

@app.route('/add_crop', methods=['GET', 'POST'])
def add_crop():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        crop_name = request.form['crop_name']
        variety = request.form['variety']
        plant_date = request.form['plant_date']
        expected_harvest = request.form['expected_harvest']
        field_location = request.form['field_location']
        area_planted = request.form['area_planted']
        status = request.form['status']
        notes = request.form['notes']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO Crops (crop_name, variety, plant_date, expected_harvest, 
               field_location, area_planted, status, notes, created_by) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (crop_name, variety, plant_date, expected_harvest, field_location, 
             area_planted, status, notes, session['user_id'])
        )
        conn.commit()
        flash('Crop added successfully!', 'success')
        return redirect(url_for('crops'))
    
    return render_template('add_crop.html')

# Sales Management
@app.route('/sales')
def sales():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Sales ORDER BY sale_date DESC')
    sales = cursor.fetchall()
    return render_template('sales.html', sales=sales)

@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        product = request.form['product']
        quantity = float(request.form['quantity'])
        unit_price = float(request.form['unit_price'])
        sale_date = request.form['sale_date']
        payment_status = request.form['payment_status']
        total_amt = quantity * unit_price
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO Sales (customer_name, product, quantity, unit_price, 
               total_amt, sale_date, payment_status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)''',
            (customer_name, product, quantity, unit_price, total_amt, sale_date, payment_status)
        )
        conn.commit()
        flash('Sale recorded successfully!', 'success')
        return redirect(url_for('sales'))
    
    return render_template('add_sale.html')

# API Routes for Data
@app.route('/api/vegetation_data')
def api_vegetation_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Vegetation ORDER BY measure_date DESC LIMIT 10')
    data = cursor.fetchall()
    return jsonify([dict(row) for row in data])

@app.route('/api/soil_analysis')
def api_soil_analysis():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Soil ORDER BY analysis_id DESC LIMIT 10')
    data = cursor.fetchall()
    return jsonify([dict(row) for row in data])

# Storage Management
@app.route('/storage')
def storage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Storage ORDER BY entry_date DESC')
    storage_items = cursor.fetchall()
    return render_template('storage.html', storage_items=storage_items)

# Livestock Management
@app.route('/livestock')
def livestock():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Livestock')
    livestock = cursor.fetchall()
    return render_template('livestock.html', livestock=livestock)

# Equipment Management
@app.route('/equipment')
def equipment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Equipment')
    equipment = cursor.fetchall()
    return render_template('equipment.html', equipment=equipment)

# Weather Data
@app.route('/weather')
def weather():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Weather ORDER BY record_date DESC LIMIT 30')
    weather_data = cursor.fetchall()
    return render_template('weather.html', weather_data=weather_data)

# Initialize database before first request
@app.before_first_request
def create_tables():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)