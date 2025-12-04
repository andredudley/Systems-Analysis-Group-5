import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
<<<<<<< HEAD
app.secret_key = 'your-secret-key-here'

# ------------------------------
# DATABASE CONNECTION
# ------------------------------
def get_db():
    return mysql.connector.connect(
        host='dudleezy.mysql.pythonanywhere-services.com',
        user='dudleezy',
        password='AtDj07092003',     # <-- REPLACE AFTER TESTING
        database='dudleezy$skyacres'
    )

# ------------------------------
# GENERIC SQL HELPERS
# ------------------------------
def fetch_all(query, params=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params or ())
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

def fetch_one(query, params=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params or ())
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result

def execute_query(query, params=None):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params or ())
    db.commit()
    cursor.close()
    db.close()


# ============================================================
# USER AUTHENTICATION
# ============================================================

=======

# Main Routes
>>>>>>> d35f19d84725a425ff98e44c569cf8aeda429f76
@app.route('/')
def index():
    return render_template('user-authentication/index.html')

<<<<<<< HEAD
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')

        user = fetch_one(
            "SELECT * FROM Users WHERE username=%s AND password=%s",
            (username, password_input)
        )

        if user:
            session['user'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('user-authentication/login.html')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email    = request.form.get('email')
        password = request.form.get('password')

        execute_query(
            "INSERT INTO Users(username, email, password) VALUES (%s, %s, %s)",
            (username, email, password)
        )

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('user-authentication/register.html')


@app.route('/dashboard/')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    # --- DASHBOARD METRICS ---

    # Crops count
    crops_count = fetch_one("SELECT COUNT(*) AS count FROM crops")['count']

    # Livestock count
    livestock_count = fetch_one("SELECT COUNT(*) AS count FROM livestock")['count']

    # Equipment count + maintenance alerts
    equipment_total = fetch_one("SELECT COUNT(*) AS count FROM equipment")['count']
    equipment_maintenance = fetch_one(
        "SELECT COUNT(*) AS count FROM equipment WHERE status='Needs Maintenance'"
    )['count']

    # Sales total revenue (this month)
    sales_revenue = fetch_one("""
        SELECT COALESCE(SUM(total_amt),0) AS total
        FROM sales
        WHERE MONTH(sale_date) = MONTH(CURRENT_DATE())
          AND YEAR(sale_date) = YEAR(CURRENT_DATE())
    """)['total']

    # Employees count
    employees_count = fetch_one("SELECT COUNT(*) AS count FROM employees")['count']

    # Storage count + low stock
    storage_total = fetch_one("SELECT COUNT(*) AS count FROM storage")['count']
    low_stock = fetch_one("SELECT COUNT(*) AS count FROM storage WHERE quantity < 10")['count']

    # Transportation count
    transportation_count = fetch_one("SELECT COUNT(*) AS count FROM transportation")['count']

    # Soil analysis count
    soil_count = fetch_one("SELECT COUNT(*) AS count FROM soil")['count']

    # Marketing campaigns count
    marketing_count = fetch_one("SELECT COUNT(*) AS count FROM marketing_campaigns")['count']

    # Vegetation count
    vegetation_count = fetch_one("SELECT COUNT(*) AS count FROM vegetation")['count']

    # Weather records
    weather_count = fetch_one("SELECT COUNT(*) AS count FROM weather")['count']

    # Yield count
    yield_count = fetch_one("SELECT COUNT(*) AS count FROM yield")['count']


    # Pass all data to template
    return render_template(
        'user-authentication/dashboard.html',
        crops_count=crops_count,
        livestock_count=livestock_count,
        equipment_total=equipment_total,
        equipment_maintenance=equipment_maintenance,
        sales_revenue=sales_revenue,
        employees_count=employees_count,
        storage_total=storage_total,
        low_stock=low_stock,
        transportation_count=transportation_count,
        soil_count=soil_count,
        marketing_count=marketing_count,
        vegetation_count=vegetation_count,
        weather_count=weather_count,
        yield_count=yield_count
    )


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))


# ============================================================
# CRUD ROUTE TEMPLATES FOR ALL TABLES
# - Each section uses:
#       fetch_all()
#       execute_query()
#       fetch_one()
# ============================================================

# -------------------- CROPS --------------------

# LIST CROPS (JOIN USERS FOR CREATED BY)
@app.route('/crops/')
def crops_list():
    rows = fetch_all("""
        SELECT c.*, u.username AS creator
        FROM crops c
        LEFT JOIN Users u ON c.created_by = u.user_id
        ORDER BY crop_id DESC
    """)
    return render_template('crops/list.html', rows=rows)


# CREATE CROP
@app.route('/crops/create', methods=['GET', 'POST'])
def crops_create():
    if request.method == 'POST':

        # Get user ID for created_by
        created_by = None
        if 'user' in session:
            user = fetch_one(
                "SELECT user_id FROM Users WHERE username=%s",
                (session['user'],)
            )
            if user:
                created_by = user['user_id']

        # Clean form fields
        crop_name = request.form['crop_name']
        variety = request.form.get('variety') or None
        plant_date = request.form['plant_date']

        expected_harvest = request.form.get('expected_harvest')
        if expected_harvest == "":
            expected_harvest = None

        field_location = request.form['field_location']

        # SAFELY convert number
        try:
            area_planted = float(request.form['area_planted'])
        except ValueError:
            flash("Area Planted must be a valid number.", "error")
            return redirect(url_for('crops_create'))

        status = request.form['status']
        notes = request.form.get('notes') or None

        # All cleaned data here
        data = (
            crop_name,
            variety,
            plant_date,
            expected_harvest,
            field_location,
            area_planted,
            status,
            notes,
            created_by
        )

        execute_query("""
            INSERT INTO crops
                (crop_name, variety, plant_date, expected_harvest,
                 field_location, area_planted, status, notes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)

        flash('Crop created successfully!', 'success')
        return redirect(url_for('crops_list'))

    return render_template('crops/create.html')



# SEARCH CROPS
@app.route('/crops/search')
def crops_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM crops
            WHERE crop_name LIKE %s
               OR variety LIKE %s
               OR field_location LIKE %s
               OR status LIKE %s
               OR notes LIKE %s
        """
        results = fetch_all(sql, (like, like, like, like, like))

    return render_template('crops/search.html', query=query, results=results)


# UPDATE CROP
@app.route('/crops/update/<int:crop_id>', methods=['GET', 'POST'])
def crops_update(crop_id):
    crop = fetch_one("SELECT * FROM crops WHERE crop_id=%s", (crop_id,))

    if not crop:
        flash("Crop not found.", "error")
        return redirect(url_for('crops_list'))

    if request.method == 'POST':

        created_by = crop['created_by']  # keep original unless updating manually

        data = (
            request.form['crop_name'],
            request.form.get('variety'),
            request.form['plant_date'],
            request.form.get('expected_harvest'),
            request.form['field_location'],
            float(request.form['area_planted']),
            request.form['status'],
            request.form.get('notes'),
            created_by,
            crop_id
        )

        execute_query("""
            UPDATE crops
            SET crop_name=%s,
                variety=%s,
                plant_date=%s,
                expected_harvest=%s,
                field_location=%s,
                area_planted=%s,
                status=%s,
                notes=%s,
                created_by=%s
            WHERE crop_id=%s
        """, data)

        flash("Crop updated successfully!", "success")
        return redirect(url_for('crops_list'))

    return render_template('crops/update.html', crop=crop)


# DELETE CROP
@app.route('/crops/delete/<int:crop_id>', methods=['POST'])
def crops_delete(crop_id):
    execute_query("DELETE FROM crops WHERE crop_id=%s", (crop_id,))
    flash("Crop deleted successfully!", "success")
    return redirect(url_for('crops_list'))


# -------------------- EMPLOYEES --------------------

# LIST EMPLOYEES
@app.route('/employees/')
def employees_list():
    rows = fetch_all("SELECT * FROM employees ORDER BY emp_id DESC")
    return render_template('employees/list.html', rows=rows)


# CREATE EMPLOYEE
@app.route('/employees/create', methods=['GET', 'POST'])
def employees_create():
    if request.method == 'POST':
        data = (
            request.form['FName'],
            request.form['LName'],
            request.form['position'],
            request.form['hire_date'],
            request.form.get('phone'),
            request.form.get('email')
        )

        execute_query("""
            INSERT INTO employees (FName, LName, position, hire_date, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, data)

        flash('Employee created successfully!', 'success')
        return redirect(url_for('employees_list'))

    return render_template('employees/create.html')


# SEARCH EMPLOYEES
@app.route('/employees/search')
def employees_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM employees
            WHERE FName LIKE %s
               OR LName LIKE %s
               OR position LIKE %s
               OR phone LIKE %s
               OR email LIKE %s
        """

        results = fetch_all(sql, (like, like, like, like, like))

    return render_template('employees/search.html', query=query, results=results)




# UPDATE EMPLOYEE
@app.route('/employees/update/<int:emp_id>', methods=['GET', 'POST'])
def employees_update(emp_id):
    employee = fetch_one("SELECT * FROM employees WHERE emp_id=%s", (emp_id,))

    if not employee:
        flash("Employee not found.", "error")
        return redirect(url_for('employees_list'))

    if request.method == 'POST':
        data = (
            request.form['FName'],
            request.form['LName'],
            request.form['position'],
            request.form['hire_date'],
            request.form.get('phone'),
            request.form.get('email'),
            emp_id
        )

        execute_query("""
            UPDATE employees
            SET FName=%s, LName=%s, position=%s, hire_date=%s, phone=%s, email=%s
            WHERE emp_id=%s
        """, data)

        flash("Employee updated successfully!", "success")
        return redirect(url_for('employees_list'))

    return render_template('employees/update.html', employee=employee)


# DELETE EMPLOYEE
@app.route('/employees/delete/<int:emp_id>', methods=['POST'])
def employees_delete(emp_id):
    execute_query("DELETE FROM employees WHERE emp_id=%s", (emp_id,))
    flash("Employee deleted successfully!", "success")
    return redirect(url_for('employees_list'))


# -------------------- EQUIPMENT --------------------

# LIST EQUIPMENT
@app.route('/equipment/')
def equipment_list():
    rows = fetch_all("SELECT * FROM equipment ORDER BY equip_id DESC")
    return render_template('equipment/list.html', rows=rows)


# CREATE EQUIPMENT
@app.route('/equipment/create', methods=['GET', 'POST'])
def equipment_create():
    if request.method == 'POST':
        data = (
            request.form['equip_name'],
            request.form['type'],
            request.form['purchase_date'],
            request.form.get('last_maintenance'),
            request.form['status'],
            request.form.get('location')
        )

        execute_query("""
            INSERT INTO equipment (equip_name, type, purchase_date, last_maintenance, status, location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, data)

        flash('Equipment created successfully!', 'success')
        return redirect(url_for('equipment_list'))

    return render_template('equipment/create.html')


# SEARCH EQUIPMENT
@app.route('/equipment/search')
def equipment_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM equipment
            WHERE equip_name LIKE %s
               OR type LIKE %s
               OR status LIKE %s
               OR location LIKE %s
        """
        results = fetch_all(sql, (like, like, like, like))

    return render_template('equipment/search.html', query=query, results=results)


# UPDATE EQUIPMENT
@app.route('/equipment/update/<int:equip_id>', methods=['GET', 'POST'])
def equipment_update(equip_id):
    equipment = fetch_one("SELECT * FROM equipment WHERE equip_id=%s", (equip_id,))

    if not equipment:
        flash("Equipment not found.", "error")
        return redirect(url_for('equipment_list'))

    if request.method == 'POST':
        data = (
            request.form['equip_name'],
            request.form['type'],
            request.form['purchase_date'],
            request.form.get('last_maintenance'),
            request.form['status'],
            request.form.get('location'),
            equip_id
        )

        execute_query("""
            UPDATE equipment
            SET equip_name=%s, type=%s, purchase_date=%s, last_maintenance=%s,
                status=%s, location=%s
            WHERE equip_id=%s
        """, data)

        flash("Equipment updated successfully!", "success")
        return redirect(url_for('equipment_list'))

    return render_template('equipment/update.html', equipment=equipment)


# DELETE EQUIPMENT
@app.route('/equipment/delete/<int:equip_id>', methods=['POST'])
def equipment_delete(equip_id):
    execute_query("DELETE FROM equipment WHERE equip_id=%s", (equip_id,))
    flash("Equipment deleted successfully!", "success")
    return redirect(url_for('equipment_list'))



# -------------------- LIVESTOCK --------------------

# LIST LIVESTOCK
@app.route('/livestock/')
def livestock_list():
    rows = fetch_all("SELECT * FROM livestock ORDER BY animal_id DESC")
    return render_template('livestock/list.html', rows=rows)


# CREATE LIVESTOCK
@app.route('/livestock/create', methods=['GET', 'POST'])
def livestock_create():
    if request.method == 'POST':
        data = (
            request.form['species'],
            request.form.get('breed'),
            request.form.get('tag_number'),
            request.form.get('birth_date'),
            request.form.get('weight'),
            request.form.get('health_status'),
            request.form.get('location')
        )

        try:
            execute_query("""
                INSERT INTO livestock (species, breed, tag_number, birth_date, weight, health_status, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, data)

            flash('Livestock record created successfully!', 'success')
            return redirect(url_for('livestock_list'))

        except Exception as e:
            # Tag number is UNIQUE → handle duplicates gracefully
            if "Duplicate entry" in str(e):
                flash("Error: Tag number already exists!", "error")
            else:
                flash(f"Database error: {str(e)}", "error")

            return redirect(url_for('livestock_create'))

    return render_template('livestock/create.html')


# SEARCH LIVESTOCK
@app.route('/livestock/search')
def livestock_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM livestock
            WHERE species LIKE %s
               OR breed LIKE %s
               OR tag_number LIKE %s
               OR health_status LIKE %s
               OR location LIKE %s
        """
        results = fetch_all(sql, (like, like, like, like, like))

    return render_template('livestock/search.html', query=query, results=results)

# UPDATE LIVESTOCK
@app.route('/livestock/update/<int:animal_id>', methods=['GET', 'POST'])
def livestock_update(animal_id):
    animal = fetch_one("SELECT * FROM livestock WHERE animal_id=%s", (animal_id,))

    if not animal:
        flash("Livestock record not found.", "error")
        return redirect(url_for('livestock_list'))

    if request.method == 'POST':
        data = (
            request.form['species'],
            request.form.get('breed'),
            request.form.get('tag_number'),
            request.form.get('birth_date'),
            request.form.get('weight'),
            request.form.get('health_status'),
            request.form.get('location'),
            animal_id
        )

        try:
            execute_query("""
                UPDATE livestock
                SET species=%s, breed=%s, tag_number=%s, birth_date=%s, weight=%s,
                    health_status=%s, location=%s
                WHERE animal_id=%s
            """, data)

            flash("Livestock record updated successfully!", "success")
            return redirect(url_for('livestock_list'))

        except Exception as e:
            if "Duplicate entry" in str(e):
                flash("Error: Tag number must be unique!", "error")
            else:
                flash(f"Database error: {str(e)}", "error")

            return redirect(url_for('livestock_update', animal_id=animal_id))

    return render_template('livestock/update.html', animal=animal)


# DELETE LIVESTOCK
@app.route('/livestock/delete/<int:animal_id>', methods=['POST'])
def livestock_delete(animal_id):
    execute_query("DELETE FROM livestock WHERE animal_id=%s", (animal_id,))
    flash("Livestock record deleted successfully!", "success")
    return redirect(url_for('livestock_list'))



# -------------------- MARKETING --------------------

# LIST MARKETING CAMPAIGNS
@app.route('/marketing/')
def marketing_list():
    rows = fetch_all("SELECT * FROM marketing_campaigns ORDER BY campaign_id DESC")
    return render_template('marketing/list.html', rows=rows)


# CREATE MARKETING CAMPAIGN
@app.route('/marketing/create', methods=['GET', 'POST'])
def marketing_create():
    if request.method == 'POST':
        data = (
            request.form['campaign_name'],
            request.form['start_date'],
            request.form.get('end_date'),
            request.form.get('budget'),
            request.form.get('target_audience'),
            request.form['status']
        )

        execute_query("""
            INSERT INTO marketing_campaigns
            (campaign_name, start_date, end_date, budget, target_audience, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, data)

        flash('Marketing campaign created successfully!', 'success')
        return redirect(url_for('marketing_list'))

    return render_template('marketing/create.html')


# SEARCH MARKETING CAMPAIGNS
@app.route('/marketing/search')
def marketing_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM marketing_campaigns
            WHERE campaign_name LIKE %s
               OR target_audience LIKE %s
               OR status LIKE %s
        """
        results = fetch_all(sql, (like, like, like))

    return render_template('marketing/search.html', query=query, results=results)



# UPDATE MARKETING CAMPAIGN
@app.route('/marketing/update/<int:campaign_id>', methods=['GET', 'POST'])
def marketing_update(campaign_id):
    campaign = fetch_one("SELECT * FROM marketing_campaigns WHERE campaign_id=%s", (campaign_id,))

    if not campaign:
        flash("Campaign not found.", "error")
        return redirect(url_for('marketing_list'))

    if request.method == 'POST':
        data = (
            request.form['campaign_name'],
            request.form['start_date'],
            request.form.get('end_date'),
            request.form.get('budget'),
            request.form.get('target_audience'),
            request.form['status'],
            campaign_id
        )

        execute_query("""
            UPDATE marketing_campaigns
            SET campaign_name=%s,
                start_date=%s,
                end_date=%s,
                budget=%s,
                target_audience=%s,
                status=%s
            WHERE campaign_id=%s
        """, data)

        flash("Campaign updated successfully!", "success")
        return redirect(url_for('marketing_list'))

    return render_template('marketing/update.html', campaign=campaign)


# DELETE MARKETING CAMPAIGN
@app.route('/marketing/delete/<int:campaign_id>', methods=['POST'])
def marketing_delete(campaign_id):
    execute_query("DELETE FROM marketing_campaigns WHERE campaign_id=%s", (campaign_id,))
    flash("Marketing campaign deleted successfully!", "success")
    return redirect(url_for('marketing_list'))


# -------------------- SALES --------------------

# LIST SALES
@app.route('/sales/')
def sales_list():
    rows = fetch_all("SELECT * FROM sales ORDER BY sale_id DESC")
    return render_template('sales/list.html', rows=rows)


# CREATE SALE
@app.route('/sales/create', methods=['GET', 'POST'])
def sales_create():
    if request.method == 'POST':
        # Pull values from form
        customer_name  = request.form['customer_name']
        product        = request.form['product']
        quantity       = float(request.form['quantity'])
        unit_price     = float(request.form['unit_price'])
        sale_date      = request.form['sale_date']
        payment_status = request.form['payment_status']

        # Compute total amount on the server to avoid bad input
        total_amt = quantity * unit_price

        data = (
            customer_name,
            product,
            quantity,
            unit_price,
            total_amt,
            sale_date,
            payment_status
        )

        execute_query("""
            INSERT INTO sales
                (customer_name, product, quantity, unit_price, total_amt, sale_date, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, data)

        flash('Sales record created successfully!', 'success')
        return redirect(url_for('sales_list'))

    return render_template('sales/create.html')


# SEARCH SALES
@app.route('/sales/search')
def sales_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM sales
            WHERE customer_name LIKE %s
               OR product LIKE %s
               OR payment_status LIKE %s
        """
        results = fetch_all(sql, (like, like, like))

    return render_template('sales/search.html', query=query, results=results)



# UPDATE SALE
@app.route('/sales/update/<int:sale_id>', methods=['GET', 'POST'])
def sales_update(sale_id):
    sale = fetch_one("SELECT * FROM sales WHERE sale_id=%s", (sale_id,))

    if not sale:
        flash("Sales record not found.", "error")
        return redirect(url_for('sales_list'))

    if request.method == 'POST':
        customer_name  = request.form['customer_name']
        product        = request.form['product']
        quantity       = float(request.form['quantity'])
        unit_price     = float(request.form['unit_price'])
        sale_date      = request.form['sale_date']
        payment_status = request.form['payment_status']

        total_amt = quantity * unit_price

        data = (
            customer_name,
            product,
            quantity,
            unit_price,
            total_amt,
            sale_date,
            payment_status,
            sale_id
        )

        execute_query("""
            UPDATE sales
            SET customer_name=%s,
                product=%s,
                quantity=%s,
                unit_price=%s,
                total_amt=%s,
                sale_date=%s,
                payment_status=%s
            WHERE sale_id=%s
        """, data)

        flash("Sales record updated successfully!", "success")
        return redirect(url_for('sales_list'))

    return render_template('sales/update.html', sale=sale)


# DELETE SALE
@app.route('/sales/delete/<int:sale_id>', methods=['POST'])
def sales_delete(sale_id):
    execute_query("DELETE FROM sales WHERE sale_id=%s", (sale_id,))
    flash("Sales record deleted successfully!", "success")
    return redirect(url_for('sales_list'))

# -------------------- SOIL --------------------

# LIST SOIL RECORDS
@app.route('/soil/')
def soil_list():
    rows = fetch_all("SELECT * FROM soil ORDER BY analysis_id DESC")
    return render_template('soil/list.html', rows=rows)


# CREATE SOIL RECORD
@app.route('/soil/create', methods=['GET', 'POST'])
def soil_create():
    if request.method == 'POST':

        data = (
            request.form['field_location'],
            request.form['test_name'],
            float(request.form['ph_level']),
            request.form.get('nitrogen') or None,
            request.form.get('phosphorus') or None,
            request.form.get('potassium') or None
        )

        execute_query("""
            INSERT INTO soil (field_location, test_name, ph_level, nitrogen, phosphorus, potassium)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, data)

        flash('Soil record created successfully!', 'success')
        return redirect(url_for('soil_list'))

    return render_template('soil/create.html')


# SEARCH SOIL RECORDS
@app.route('/soil/search')
def soil_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM soil
            WHERE field_location LIKE %s
               OR test_name LIKE %s
        """
        results = fetch_all(sql, (like, like))

    return render_template('soil/search.html', query=query, results=results)



# UPDATE SOIL RECORD
@app.route('/soil/update/<int:analysis_id>', methods=['GET', 'POST'])
def soil_update(analysis_id):
    soil_row = fetch_one("SELECT * FROM soil WHERE analysis_id=%s", (analysis_id,))

    if not soil_row:
        flash("Soil record not found.", "error")
        return redirect(url_for('soil_list'))

    if request.method == 'POST':
        data = (
            request.form['field_location'],
            request.form['test_name'],
            float(request.form['ph_level']),
            request.form.get('nitrogen') or None,
            request.form.get('phosphorus') or None,
            request.form.get('potassium') or None,
            analysis_id
        )

        execute_query("""
            UPDATE soil
            SET field_location=%s,
                test_name=%s,
                ph_level=%s,
                nitrogen=%s,
                phosphorus=%s,
                potassium=%s
            WHERE analysis_id=%s
        """, data)

        flash("Soil record updated successfully!", "success")
        return redirect(url_for('soil_list'))

    return render_template('soil/update.html', soil=soil_row)


# DELETE SOIL RECORD
@app.route('/soil/delete/<int:analysis_id>', methods=['POST'])
def soil_delete(analysis_id):
    execute_query("DELETE FROM soil WHERE analysis_id=%s", (analysis_id,))
    flash("Soil record deleted successfully!", "success")
    return redirect(url_for('soil_list'))



# -------------------- STORAGE --------------------

# LIST STORAGE RECORDS
@app.route('/storage/')
def storage_list():
    # Safely select all columns; note the backticks around `condition`
    sql = """
        SELECT
            Storage_id,
            product_name,
            quantity,
            unit,
            storage_location,
            entry_date,
            `condition`
        FROM storage
    """
    rows = fetch_all(sql)
    return render_template('storage/list.html', rows=rows)



# CREATE STORAGE RECORD
@app.route('/storage/create', methods=['GET', 'POST'])
def storage_create():
    if request.method == 'POST':
        data = (
            request.form['product_name'],
            float(request.form['quantity']),
            request.form['unit'],
            request.form['storage_location'],
            request.form['entry_date'],
            request.form.get('condition')
        )

        execute_query("""
            INSERT INTO storage (product_name, quantity, unit, storage_location, entry_date, condition)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, data)

        flash('Storage record created successfully!', 'success')
        return redirect(url_for('storage_list'))

    return render_template('storage/create.html')


# SEARCH STORAGE RECORDS
@app.route('/storage/search')
def storage_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM storage
            WHERE product_name LIKE %s
               OR storage_location LIKE %s
               OR condition LIKE %s
        """
        results = fetch_all(sql, (like, like, like))

    return render_template('storage/search.html', query=query, results=results)

# UPDATE STORAGE RECORD
@app.route('/storage/update/<int:Storage_id>', methods=['GET', 'POST'])
def storage_update(Storage_id):
    record = fetch_one("SELECT * FROM storage WHERE Storage_id=%s", (Storage_id,))

    if not record:
        flash("Storage record not found.", "error")
        return redirect(url_for('storage_list'))

    if request.method == 'POST':
        data = (
            request.form['product_name'],
            float(request.form['quantity']),
            request.form['unit'],
            request.form['storage_location'],
            request.form['entry_date'],
            request.form.get('condition'),
            Storage_id
        )

        execute_query("""
            UPDATE storage
            SET product_name=%s,
                quantity=%s,
                unit=%s,
                storage_location=%s,
                entry_date=%s,
                condition=%s
            WHERE Storage_id=%s
        """, data)

        flash("Storage record updated successfully!", "success")
        return redirect(url_for('storage_list'))

    return render_template('storage/update.html', record=record)


# DELETE STORAGE RECORD
@app.route('/storage/delete/<int:Storage_id>', methods=['POST'])
def storage_delete(Storage_id):
    execute_query("DELETE FROM storage WHERE Storage_id=%s", (Storage_id,))
    flash("Storage record deleted successfully!", "success")
    return redirect(url_for('storage_list'))


# -------------------- TRANSPORTATION --------------------

# LIST TRANSPORTATION RECORDS
@app.route('/transportation/')
def transportation_list():
    rows = fetch_all("SELECT * FROM transportation ORDER BY transport_id DESC")
    return render_template('transportation/list.html', rows=rows)


# CREATE TRANSPORTATION RECORD
@app.route('/transportation/create', methods=['GET', 'POST'])
def transportation_create():
    if request.method == 'POST':

        data = (
            request.form['vehicle_id'],
            request.form['driver_name'],
            request.form['route'],
            request.form['depart_date'],     # datetime (YYYY-MM-DD HH:MM:SS)
            request.form.get('arrive_date'), # nullable datetime
            request.form.get('cargo_date'),  # nullable date
            request.form['status']
        )

        execute_query("""
            INSERT INTO transportation
            (vehicle_id, driver_name, route, depart_date, arrive_date, cargo_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, data)

        flash('Transportation record created successfully!', 'success')
        return redirect(url_for('transportation_list'))

    return render_template('transportation/create.html')


# SEARCH TRANSPORTATION RECORDS
@app.route('/transportation/search')
def transportation_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM transportation
            WHERE vehicle_id LIKE %s
               OR driver_name LIKE %s
               OR route LIKE %s
               OR status LIKE %s
        """
        results = fetch_all(sql, (like, like, like, like))

    return render_template('transportation/search.html', query=query, results=results)



# UPDATE TRANSPORTATION RECORD
@app.route('/transportation/update/<int:transport_id>', methods=['GET', 'POST'])
def transportation_update(transport_id):
    record = fetch_one("SELECT * FROM transportation WHERE transport_id=%s", (transport_id,))

    if not record:
        flash("Transportation record not found.", "error")
        return redirect(url_for('transportation_list'))

    if request.method == 'POST':
        data = (
            request.form['vehicle_id'],
            request.form['driver_name'],
            request.form['route'],
            request.form['depart_date'],
            request.form.get('arrive_date'),
            request.form.get('cargo_date'),
            request.form['status'],
            transport_id
        )

        execute_query("""
            UPDATE transportation
            SET vehicle_id=%s,
                driver_name=%s,
                route=%s,
                depart_date=%s,
                arrive_date=%s,
                cargo_date=%s,
                status=%s
            WHERE transport_id=%s
        """, data)

        flash('Transportation record updated successfully!', 'success')
        return redirect(url_for('transportation_list'))

    return render_template('transportation/update.html', record=record)


# DELETE TRANSPORTATION RECORD
@app.route('/transportation/delete/<int:transport_id>', methods=['POST'])
def transportation_delete(transport_id):
    execute_query("DELETE FROM transportation WHERE transport_id=%s", (transport_id,))
    flash("Transportation record deleted successfully!", "success")
    return redirect(url_for('transportation_list'))



# -------------------- VEGETATION --------------------

# LIST VEGETATION RECORDS
@app.route('/vegetation/')
def vegetation_list():
    rows = fetch_all("SELECT * FROM vegetation ORDER BY vi_id DESC")
    return render_template('vegetation/list.html', rows=rows)


# CREATE VEGETATION RECORD
@app.route('/vegetation/create', methods=['GET', 'POST'])
def vegetation_create():
    if request.method == 'POST':

        data = (
            request.form['field_location'],
            request.form['measure_date'],
            float(request.form['ndvi_value']),
            request.form['crop_health'],
            request.form.get('notes')
        )

        execute_query("""
            INSERT INTO vegetation (field_location, measure_date, ndvi_value, crop_health, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, data)

        flash('Vegetation record created successfully!', 'success')
        return redirect(url_for('vegetation_list'))

    return render_template('vegetation/create.html')


# SEARCH VEGETATION RECORDS
@app.route('/vegetation/search')
def vegetation_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM vegetation
            WHERE field_location LIKE %s
               OR crop_health LIKE %s
               OR notes LIKE %s
        """
        results = fetch_all(sql, (like, like, like))

    return render_template('vegetation/search.html', query=query, results=results)



# UPDATE VEGETATION RECORD
@app.route('/vegetation/update/<int:vi_id>', methods=['GET', 'POST'])
def vegetation_update(vi_id):
    record = fetch_one("SELECT * FROM vegetation WHERE vi_id=%s", (vi_id,))

    if not record:
        flash("Vegetation record not found.", "error")
        return redirect(url_for('vegetation_list'))

    if request.method == 'POST':
        data = (
            request.form['field_location'],
            request.form['measure_date'],
            float(request.form['ndvi_value']),
            request.form['crop_health'],
            request.form.get('notes'),
            vi_id
        )

        execute_query("""
            UPDATE vegetation
            SET field_location=%s,
                measure_date=%s,
                ndvi_value=%s,
                crop_health=%s,
                notes=%s
            WHERE vi_id=%s
        """, data)

        flash("Vegetation record updated successfully!", "success")
        return redirect(url_for('vegetation_list'))

    return render_template('vegetation/update.html', record=record)


# DELETE VEGETATION RECORD
@app.route('/vegetation/delete/<int:vi_id>', methods=['POST'])
def vegetation_delete(vi_id):
    execute_query("DELETE FROM vegetation WHERE vi_id=%s", (vi_id,))
    flash("Vegetation record deleted successfully!", "success")
    return redirect(url_for('vegetation_list'))



# -------------------- WEATHER --------------------

# LIST WEATHER RECORDS
@app.route('/weather/')
def weather_list():
    rows = fetch_all("SELECT * FROM weather ORDER BY weather_id DESC")
    return render_template('weather/list.html', rows=rows)


# CREATE WEATHER RECORD
@app.route('/weather/create', methods=['GET', 'POST'])
def weather_create():
    if request.method == 'POST':

        data = (
            request.form['record_date'],
            request.form.get('temp_low') or None,
            request.form.get('rainfall') or None,
            request.form.get('humidity') or None,
            request.form.get('wind_speed') or None
        )

        execute_query("""
            INSERT INTO weather (record_date, temp_low, rainfall, humidity, wind_speed)
            VALUES (%s, %s, %s, %s, %s)
        """, data)

        flash('Weather record created successfully!', 'success')
        return redirect(url_for('weather_list'))

    return render_template('weather/create.html')


# SEARCH WEATHER RECORDS
@app.route('/weather/search')
def weather_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM weather
            WHERE record_date LIKE %s
               OR temp_low LIKE %s
               OR rainfall LIKE %s
               OR humidity LIKE %s
               OR wind_speed LIKE %s
        """
        results = fetch_all(sql, (like, like, like, like, like))

    return render_template('weather/search.html', query=query, results=results)


# UPDATE WEATHER RECORD
@app.route('/weather/update/<int:weather_id>', methods=['GET', 'POST'])
def weather_update(weather_id):
    record = fetch_one("SELECT * FROM weather WHERE weather_id=%s", (weather_id,))

    if not record:
        flash("Weather record not found.", "error")
        return redirect(url_for('weather_list'))

    if request.method == 'POST':
        data = (
            request.form['record_date'],
            request.form.get('temp_low') or None,
            request.form.get('rainfall') or None,
            request.form.get('humidity') or None,
            request.form.get('wind_speed') or None,
            weather_id
        )

        execute_query("""
            UPDATE weather
            SET record_date=%s,
                temp_low=%s,
                rainfall=%s,
                humidity=%s,
                wind_speed=%s
            WHERE weather_id=%s
        """, data)

        flash("Weather record updated successfully!", "success")
        return redirect(url_for('weather_list'))

    return render_template('weather/update.html', record=record)


# DELETE WEATHER RECORD
@app.route('/weather/delete/<int:weather_id>', methods=['POST'])
def weather_delete(weather_id):
    execute_query("DELETE FROM weather WHERE weather_id=%s", (weather_id,))
    flash("Weather record deleted successfully!", "success")
    return redirect(url_for('weather_list'))



# -------------------- YIELD --------------------


# LIST YIELD RECORDS (JOIN CROPS)
@app.route('/yield/')
def yield_list():
    rows = fetch_all("""
        SELECT y.*, c.crop_name
        FROM yield y
        JOIN crops c ON y.crop_id = c.crop_id
        ORDER BY y.estimate_id DESC
    """)
    return render_template('yield/list.html', rows=rows)


@app.route('/yield/create', methods=['GET', 'POST'])
def yield_create():
    crops = fetch_all("SELECT crop_id, crop_name FROM crops ORDER BY crop_name ASC")

    if request.method == 'POST':

        # Required values
        crop_id = request.form['crop_id']
        estimated_yield = float(request.form['estimated_yield'])
        estimated_date = request.form['estimated_date']

        # Optional numeric values (actual_yield, variance)
        actual = request.form.get('actual_yield')
        variance = request.form.get('variance')

        actual_yield = float(actual) if actual else None
        variance_value = float(variance) if variance else None

        data = (
            crop_id,
            estimated_yield,
            estimated_date,
            actual_yield,
            variance_value
        )

        execute_query("""
            INSERT INTO yield (crop_id, estimated_yield, estimated_date, actual_yield, variance)
            VALUES (%s, %s, %s, %s, %s)
        """, data)

        flash('Yield estimate created successfully!', 'success')
        return redirect(url_for('yield_list'))

    return render_template('yield/create.html', crops=crops)


# SEARCH YIELD RECORDS
@app.route('/yield/search')
def yield_search():
    query = request.args.get('q', '').strip()
    results = []

    if query:
        like = f"%{query}%"
        sql = """
            SELECT *
            FROM yield
            WHERE estimated_yield LIKE %s
               OR actual_yield LIKE %s
               OR variance LIKE %s
               OR crop_id LIKE %s
        """
        results = fetch_all(sql, (like, like, like, like))

    return render_template('yield/search.html', query=query, results=results)


# UPDATE YIELD RECORD
@app.route('/yield/update/<int:estimate_id>', methods=['GET', 'POST'])
def yield_update(estimate_id):
    # fetch record
    record = fetch_one("""
        SELECT * FROM yield WHERE estimate_id=%s
    """, (estimate_id,))

    if not record:
        flash("Yield estimate not found.", "error")
        return redirect(url_for('yield_list'))

    crops = fetch_all("SELECT crop_id, crop_name FROM crops ORDER BY crop_name ASC")

    if request.method == 'POST':
        data = (
            request.form['crop_id'],
            float(request.form['estimated_yield']),
            request.form['estimated_date'],
            request.form.get('actual_yield') or None,
            request.form.get('variance') or None,
            estimate_id
        )

        execute_query("""
            UPDATE yield
            SET crop_id=%s,
                estimated_yield=%s,
                estimated_date=%s,
                actual_yield=%s,
                variance=%s
            WHERE estimate_id=%s
        """, data)

        flash("Yield record updated successfully!", "success")
        return redirect(url_for('yield_list'))

    return render_template('yield/update.html', record=record, crops=crops)


# DELETE YIELD RECORD
@app.route('/yield/delete/<int:estimate_id>', methods=['POST'])
def yield_delete(estimate_id):
    execute_query("DELETE FROM yield WHERE estimate_id=%s", (estimate_id,))
    flash("Yield record deleted successfully!", "success")
    return redirect(url_for('yield_list'))



# ------------------------------
# RUN APP
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
=======
>>>>>>> d35f19d84725a425ff98e44c569cf8aeda429f76
