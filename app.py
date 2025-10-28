from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sky_acres.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Vegetation(db.Model):
    vi_id = db.Column(db.Integer, primary_key=True)
    field_location = db.Column(db.String(100), nullable=False)
    measure_date = db.Column(db.Date, nullable=False)
    ndvi_value = db.Column(db.Float, nullable=False)
    crop_health = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)

class Employees(db.Model):
    emp_id = db.Column(db.Integer, primary_key=True)
    FName = db.Column(db.String(50), nullable=False)
    LName = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))

class Soil(db.Model):
    analysis_id = db.Column(db.Integer, primary_key=True)
    field_location = db.Column(db.String(100), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    ph_level = db.Column(db.Float, nullable=False)
    nitrogen = db.Column(db.Float)
    phosphorus = db.Column(db.Float)
    potassium = db.Column(db.Float)

class Storage(db.Model):
    Storage_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    storage_location = db.Column(db.String(100), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    condition = db.Column(db.String(50))

class Sales(db.Model):
    sale_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amt = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    payment_status = db.Column(db.String(20), nullable=False)

class Crops(db.Model):
    crop_id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    variety = db.Column(db.String(100))
    plant_date = db.Column(db.Date, nullable=False)
    expected_harvest = db.Column(db.Date)
    field_location = db.Column(db.String(100), nullable=False)
    area_planted = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))

class Livestock(db.Model):
    animal_id = db.Column(db.Integer, primary_key=True)
    species = db.Column(db.String(50), nullable=False)
    breed = db.Column(db.String(50))
    tag_number = db.Column(db.String(50), unique=True)
    birth_date = db.Column(db.Date)
    weight = db.Column(db.Float)
    health_status = db.Column(db.String(50))
    location = db.Column(db.String(100))

class Equipment(db.Model):
    equip_id = db.Column(db.Integer, primary_key=True)
    equip_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.Date, nullable=False)
    last_maintenance = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))

class Weather(db.Model):
    weather_id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.Date, nullable=False)
    temp_low = db.Column(db.Float)
    rainfall = db.Column(db.Float)
    humidity = db.Column(db.Float)
    wind_speed = db.Column(db.Float)

class MarketingCampaigns(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True)
    campaign_name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Float)
    target_audience = db.Column(db.String(200))
    status = db.Column(db.String(50), nullable=False)

class Transportation(db.Model):
    transport_id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.String(50), nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    route = db.Column(db.String(200), nullable=False)
    depart_date = db.Column(db.DateTime, nullable=False)
    arrive_date = db.Column(db.DateTime)
    cargo_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False)

class Yield(db.Model):
    estimate_id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crops.crop_id'), nullable=False)
    estimated_yield = db.Column(db.Float, nullable=False)
    estimated_date = db.Column(db.Date, nullable=False)
    actual_yield = db.Column(db.Float)
    variance = db.Column(db.Float)

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Main Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add authentication logic here
        user = Users.query.filter_by(username=username).first()
        if user and user.password == password:  # In production, use proper password hashing
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Vegetation Routes
@app.route('/vegetation')
def vegetation_list():
    vegetation_data = Vegetation.query.all()
    return render_template('vegetation/list.html', vegetation=vegetation_data)

@app.route('/vegetation/create', methods=['GET', 'POST'])
def vegetation_create():
    if request.method == 'POST':
        new_vegetation = Vegetation(
            field_location=request.form['field_location'],
            measure_date=datetime.strptime(request.form['measure_date'], '%Y-%m-%d'),
            ndvi_value=float(request.form['ndvi_value']),
            crop_health=request.form['crop_health'],
            notes=request.form.get('notes', '')
        )
        db.session.add(new_vegetation)
        db.session.commit()
        flash('Vegetation data added successfully!', 'success')
        return redirect(url_for('vegetation_list'))
    return render_template('vegetation/create.html')

@app.route('/vegetation/search')
def vegetation_search():
    query = request.args.get('q', '')
    if query:
        results = Vegetation.query.filter(
            Vegetation.field_location.contains(query) |
            Vegetation.crop_health.contains(query)
        ).all()
    else:
        results = []
    return render_template('vegetation/search.html', results=results, query=query)

@app.route('/vegetation/update/<int:id>', methods=['GET', 'POST'])
def vegetation_update(id):
    vegetation = Vegetation.query.get_or_404(id)
    if request.method == 'POST':
        vegetation.field_location = request.form['field_location']
        vegetation.measure_date = datetime.strptime(request.form['measure_date'], '%Y-%m-%d')
        vegetation.ndvi_value = float(request.form['ndvi_value'])
        vegetation.crop_health = request.form['crop_health']
        vegetation.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Vegetation data updated successfully!', 'success')
        return redirect(url_for('vegetation_list'))
    return render_template('vegetation/update.html', vegetation=vegetation)

@app.route('/vegetation/delete/<int:id>', methods=['GET', 'POST'])
def vegetation_delete(id):
    vegetation = Vegetation.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(vegetation)
        db.session.commit()
        flash('Vegetation data deleted successfully!', 'success')
        return redirect(url_for('vegetation_list'))
    return render_template('vegetation/delete.html', vegetation=vegetation)

# Employees Routes
@app.route('/employees')
def employees_list():
    employees_data = Employees.query.all()
    return render_template('employees/list.html', employees=employees_data)

@app.route('/employees/create', methods=['GET', 'POST'])
def employees_create():
    if request.method == 'POST':
        new_employee = Employees(
            FName=request.form['FName'],
            LName=request.form['LName'],
            position=request.form['position'],
            hire_date=datetime.strptime(request.form['hire_date'], '%Y-%m-%d'),
            phone=request.form.get('phone', ''),
            email=request.form.get('email', '')
        )
        db.session.add(new_employee)
        db.session.commit()
        flash('Employee added successfully!', 'success')
        return redirect(url_for('employees_list'))
    return render_template('employees/create.html')

@app.route('/employees/search')
def employees_search():
    query = request.args.get('q', '')
    if query:
        results = Employees.query.filter(
            Employees.FName.contains(query) |
            Employees.LName.contains(query) |
            Employees.position.contains(query)
        ).all()
    else:
        results = []
    return render_template('employees/search.html', results=results, query=query)

@app.route('/employees/update/<int:id>', methods=['GET', 'POST'])
def employees_update(id):
    employee = Employees.query.get_or_404(id)
    if request.method == 'POST':
        employee.FName = request.form['FName']
        employee.LName = request.form['LName']
        employee.position = request.form['position']
        employee.hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d')
        employee.phone = request.form.get('phone', '')
        employee.email = request.form.get('email', '')
        db.session.commit()
        flash('Employee updated successfully!', 'success')
        return redirect(url_for('employees_list'))
    return render_template('employees/update.html', employee=employee)

@app.route('/employees/delete/<int:id>', methods=['GET', 'POST'])
def employees_delete(id):
    employee = Employees.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully!', 'success')
        return redirect(url_for('employees_list'))
    return render_template('employees/delete.html', employee=employee)

# Soil Routes
@app.route('/soil')
def soil_list():
    soil_data = Soil.query.all()
    return render_template('soil/list.html', soil_data=soil_data)

@app.route('/soil/create', methods=['GET', 'POST'])
def soil_create():
    if request.method == 'POST':
        new_soil = Soil(
            field_location=request.form['field_location'],
            test_name=request.form['test_name'],
            ph_level=float(request.form['ph_level']),
            nitrogen=float(request.form.get('nitrogen', 0)) if request.form.get('nitrogen') else None,
            phosphorus=float(request.form.get('phosphorus', 0)) if request.form.get('phosphorus') else None,
            potassium=float(request.form.get('potassium', 0)) if request.form.get('potassium') else None
        )
        db.session.add(new_soil)
        db.session.commit()
        flash('Soil analysis added successfully!', 'success')
        return redirect(url_for('soil_list'))
    return render_template('soil/create.html')

@app.route('/soil/search')
def soil_search():
    query = request.args.get('q', '')
    if query:
        results = Soil.query.filter(
            Soil.field_location.contains(query) |
            Soil.test_name.contains(query)
        ).all()
    else:
        results = []
    return render_template('soil/search.html', results=results, query=query)

@app.route('/soil/update/<int:id>', methods=['GET', 'POST'])
def soil_update(id):
    soil = Soil.query.get_or_404(id)
    if request.method == 'POST':
        soil.field_location = request.form['field_location']
        soil.test_name = request.form['test_name']
        soil.ph_level = float(request.form['ph_level'])
        soil.nitrogen = float(request.form.get('nitrogen', 0)) if request.form.get('nitrogen') else None
        soil.phosphorus = float(request.form.get('phosphorus', 0)) if request.form.get('phosphorus') else None
        soil.potassium = float(request.form.get('potassium', 0)) if request.form.get('potassium') else None
        db.session.commit()
        flash('Soil analysis updated successfully!', 'success')
        return redirect(url_for('soil_list'))
    return render_template('soil/update.html', soil=soil)

@app.route('/soil/delete/<int:id>', methods=['GET', 'POST'])
def soil_delete(id):
    soil = Soil.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(soil)
        db.session.commit()
        flash('Soil analysis deleted successfully!', 'success')
        return redirect(url_for('soil_list'))
    return render_template('soil/delete.html', soil=soil)

# Storage Routes
@app.route('/storage')
def storage_list():
    storage_data = Storage.query.all()
    return render_template('storage/list.html', storage=storage_data)

@app.route('/storage/create', methods=['GET', 'POST'])
def storage_create():
    if request.method == 'POST':
        new_storage = Storage(
            product_name=request.form['product_name'],
            quantity=float(request.form['quantity']),
            unit=request.form['unit'],
            storage_location=request.form['storage_location'],
            entry_date=datetime.strptime(request.form['entry_date'], '%Y-%m-%d'),
            condition=request.form.get('condition', 'Good')
        )
        db.session.add(new_storage)
        db.session.commit()
        flash('Storage item added successfully!', 'success')
        return redirect(url_for('storage_list'))
    return render_template('storage/create.html')

@app.route('/storage/search')
def storage_search():
    query = request.args.get('q', '')
    if query:
        results = Storage.query.filter(
            Storage.product_name.contains(query) |
            Storage.storage_location.contains(query)
        ).all()
    else:
        results = []
    return render_template('storage/search.html', results=results, query=query)

@app.route('/storage/update/<int:id>', methods=['GET', 'POST'])
def storage_update(id):
    storage_item = Storage.query.get_or_404(id)
    if request.method == 'POST':
        storage_item.product_name = request.form['product_name']
        storage_item.quantity = float(request.form['quantity'])
        storage_item.unit = request.form['unit']
        storage_item.storage_location = request.form['storage_location']
        storage_item.entry_date = datetime.strptime(request.form['entry_date'], '%Y-%m-%d')
        storage_item.condition = request.form.get('condition', 'Good')
        db.session.commit()
        flash('Storage item updated successfully!', 'success')
        return redirect(url_for('storage_list'))
    return render_template('storage/update.html', storage=storage_item)

@app.route('/storage/delete/<int:id>', methods=['GET', 'POST'])
def storage_delete(id):
    storage_item = Storage.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(storage_item)
        db.session.commit()
        flash('Storage item deleted successfully!', 'success')
        return redirect(url_for('storage_list'))
    return render_template('storage/delete.html', storage=storage_item)

# Sales Routes
@app.route('/sales')
def sales_list():
    sales_data = Sales.query.all()
    return render_template('sales/list.html', sales=sales_data)

@app.route('/sales/create', methods=['GET', 'POST'])
def sales_create():
    if request.method == 'POST':
        new_sale = Sales(
            customer_name=request.form['customer_name'],
            product=request.form['product'],
            quantity=float(request.form['quantity']),
            unit_price=float(request.form['unit_price']),
            total_amt=float(request.form['total_amt']),
            sale_date=datetime.strptime(request.form['sale_date'], '%Y-%m-%d'),
            payment_status=request.form['payment_status']
        )
        db.session.add(new_sale)
        db.session.commit()
        flash('Sale added successfully!', 'success')
        return redirect(url_for('sales_list'))
    return render_template('sales/create.html')

@app.route('/sales/search')
def sales_search():
    query = request.args.get('q', '')
    if query:
        results = Sales.query.filter(
            Sales.customer_name.contains(query) |
            Sales.product.contains(query)
        ).all()
    else:
        results = []
    return render_template('sales/search.html', results=results, query=query)

@app.route('/sales/update/<int:id>', methods=['GET', 'POST'])
def sales_update(id):
    sale = Sales.query.get_or_404(id)
    if request.method == 'POST':
        sale.customer_name = request.form['customer_name']
        sale.product = request.form['product']
        sale.quantity = float(request.form['quantity'])
        sale.unit_price = float(request.form['unit_price'])
        sale.total_amt = float(request.form['total_amt'])
        sale.sale_date = datetime.strptime(request.form['sale_date'], '%Y-%m-%d')
        sale.payment_status = request.form['payment_status']
        db.session.commit()
        flash('Sale updated successfully!', 'success')
        return redirect(url_for('sales_list'))
    return render_template('sales/update.html', sale=sale)

@app.route('/sales/delete/<int:id>', methods=['GET', 'POST'])
def sales_delete(id):
    sale = Sales.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(sale)
        db.session.commit()
        flash('Sale deleted successfully!', 'success')
        return redirect(url_for('sales_list'))
    return render_template('sales/delete.html', sale=sale)

# Crops Routes
@app.route('/crops')
def crops_list():
    crops_data = Crops.query.all()
    return render_template('crops/list.html', crops=crops_data)

@app.route('/crops/create', methods=['GET', 'POST'])
def crops_create():
    if request.method == 'POST':
        new_crop = Crops(
            crop_name=request.form['crop_name'],
            variety=request.form.get('variety', ''),
            plant_date=datetime.strptime(request.form['plant_date'], '%Y-%m-%d'),
            expected_harvest=datetime.strptime(request.form['expected_harvest'], '%Y-%m-%d') if request.form.get('expected_harvest') else None,
            field_location=request.form['field_location'],
            area_planted=float(request.form['area_planted']),
            status=request.form['status'],
            notes=request.form.get('notes', ''),
            created_by=int(request.form['created_by'])
        )
        db.session.add(new_crop)
        db.session.commit()
        flash('Crop added successfully!', 'success')
        return redirect(url_for('crops_list'))
    return render_template('crops/create.html')

@app.route('/crops/search')
def crops_search():
    query = request.args.get('q', '')
    if query:
        results = Crops.query.filter(
            Crops.crop_name.contains(query) |
            Crops.field_location.contains(query)
        ).all()
    else:
        results = []
    return render_template('crops/search.html', results=results, query=query)

@app.route('/crops/update/<int:id>', methods=['GET', 'POST'])
def crops_update(id):
    crop = Crops.query.get_or_404(id)
    if request.method == 'POST':
        crop.crop_name = request.form['crop_name']
        crop.variety = request.form.get('variety', '')
        crop.plant_date = datetime.strptime(request.form['plant_date'], '%Y-%m-%d')
        crop.expected_harvest = datetime.strptime(request.form['expected_harvest'], '%Y-%m-%d') if request.form.get('expected_harvest') else None
        crop.field_location = request.form['field_location']
        crop.area_planted = float(request.form['area_planted'])
        crop.status = request.form['status']
        crop.notes = request.form.get('notes', '')
        crop.created_by = int(request.form['created_by'])
        db.session.commit()
        flash('Crop updated successfully!', 'success')
        return redirect(url_for('crops_list'))
    return render_template('crops/update.html', crop=crop)

@app.route('/crops/delete/<int:id>', methods=['GET', 'POST'])
def crops_delete(id):
    crop = Crops.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(crop)
        db.session.commit()
        flash('Crop deleted successfully!', 'success')
        return redirect(url_for('crops_list'))
    return render_template('crops/delete.html', crop=crop)

# Livestock Routes
@app.route('/livestock')
def livestock_list():
    livestock_data = Livestock.query.all()
    return render_template('livestock/list.html', livestock=livestock_data)

@app.route('/livestock/create', methods=['GET', 'POST'])
def livestock_create():
    if request.method == 'POST':
        new_animal = Livestock(
            species=request.form['species'],
            breed=request.form.get('breed', ''),
            tag_number=request.form.get('tag_number', ''),
            birth_date=datetime.strptime(request.form['birth_date'], '%Y-%m-%d') if request.form.get('birth_date') else None,
            weight=float(request.form['weight']) if request.form.get('weight') else None,
            health_status=request.form.get('health_status', 'Good'),
            location=request.form.get('location', '')
        )
        db.session.add(new_animal)
        db.session.commit()
        flash('Animal added successfully!', 'success')
        return redirect(url_for('livestock_list'))
    return render_template('livestock/create.html')

@app.route('/livestock/search')
def livestock_search():
    query = request.args.get('q', '')
    if query:
        results = Livestock.query.filter(
            Livestock.species.contains(query) |
            Livestock.breed.contains(query) |
            Livestock.tag_number.contains(query)
        ).all()
    else:
        results = []
    return render_template('livestock/search.html', results=results, query=query)

@app.route('/livestock/update/<int:id>', methods=['GET', 'POST'])
def livestock_update(id):
    animal = Livestock.query.get_or_404(id)
    if request.method == 'POST':
        animal.species = request.form['species']
        animal.breed = request.form.get('breed', '')
        animal.tag_number = request.form.get('tag_number', '')
        animal.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d') if request.form.get('birth_date') else None
        animal.weight = float(request.form['weight']) if request.form.get('weight') else None
        animal.health_status = request.form.get('health_status', 'Good')
        animal.location = request.form.get('location', '')
        db.session.commit()
        flash('Animal updated successfully!', 'success')
        return redirect(url_for('livestock_list'))
    return render_template('livestock/update.html', animal=animal)

@app.route('/livestock/delete/<int:id>', methods=['GET', 'POST'])
def livestock_delete(id):
    animal = Livestock.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(animal)
        db.session.commit()
        flash('Animal deleted successfully!', 'success')
        return redirect(url_for('livestock_list'))
    return render_template('livestock/delete.html', animal=animal)

# Equipment Routes
@app.route('/equipment')
def equipment_list():
    equipment_data = Equipment.query.all()
    return render_template('equipment/list.html', equipment=equipment_data)

@app.route('/equipment/create', methods=['GET', 'POST'])
def equipment_create():
    if request.method == 'POST':
        new_equipment = Equipment(
            equip_name=request.form['equip_name'],
            type=request.form['type'],
            purchase_date=datetime.strptime(request.form['purchase_date'], '%Y-%m-%d'),
            last_maintenance=datetime.strptime(request.form['last_maintenance'], '%Y-%m-%d') if request.form.get('last_maintenance') else None,
            status=request.form['status'],
            location=request.form.get('location', '')
        )
        db.session.add(new_equipment)
        db.session.commit()
        flash('Equipment added successfully!', 'success')
        return redirect(url_for('equipment_list'))
    return render_template('equipment/create.html')

@app.route('/equipment/search')
def equipment_search():
    query = request.args.get('q', '')
    if query:
        results = Equipment.query.filter(
            Equipment.equip_name.contains(query) |
            Equipment.type.contains(query)
        ).all()
    else:
        results = []
    return render_template('equipment/search.html', results=results, query=query)

@app.route('/equipment/update/<int:id>', methods=['GET', 'POST'])
def equipment_update(id):
    equipment = Equipment.query.get_or_404(id)
    if request.method == 'POST':
        equipment.equip_name = request.form['equip_name']
        equipment.type = request.form['type']
        equipment.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d')
        equipment.last_maintenance = datetime.strptime(request.form['last_maintenance'], '%Y-%m-%d') if request.form.get('last_maintenance') else None
        equipment.status = request.form['status']
        equipment.location = request.form.get('location', '')
        db.session.commit()
        flash('Equipment updated successfully!', 'success')
        return redirect(url_for('equipment_list'))
    return render_template('equipment/update.html', equipment=equipment)

@app.route('/equipment/delete/<int:id>', methods=['GET', 'POST'])
def equipment_delete(id):
    equipment = Equipment.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(equipment)
        db.session.commit()
        flash('Equipment deleted successfully!', 'success')
        return redirect(url_for('equipment_list'))
    return render_template('equipment/delete.html', equipment=equipment)

# Weather Routes
@app.route('/weather')
def weather_list():
    weather_data = Weather.query.all()
    return render_template('weather/list.html', weather_data=weather_data)

@app.route('/weather/create', methods=['GET', 'POST'])
def weather_create():
    if request.method == 'POST':
        new_weather = Weather(
            record_date=datetime.strptime(request.form['record_date'], '%Y-%m-%d'),
            temp_low=float(request.form['temp_low']) if request.form.get('temp_low') else None,
            rainfall=float(request.form['rainfall']) if request.form.get('rainfall') else None,
            humidity=float(request.form['humidity']) if request.form.get('humidity') else None,
            wind_speed=float(request.form['wind_speed']) if request.form.get('wind_speed') else None
        )
        db.session.add(new_weather)
        db.session.commit()
        flash('Weather record added successfully!', 'success')
        return redirect(url_for('weather_list'))
    return render_template('weather/create.html')

@app.route('/weather/search')
def weather_search():
    query = request.args.get('q', '')
    if query:
        try:
            search_date = datetime.strptime(query, '%Y-%m-%d')
            results = Weather.query.filter(Weather.record_date == search_date).all()
        except ValueError:
            results = []
    else:
        results = []
    return render_template('weather/search.html', results=results, query=query)

@app.route('/weather/update/<int:id>', methods=['GET', 'POST'])
def weather_update(id):
    weather = Weather.query.get_or_404(id)
    if request.method == 'POST':
        weather.record_date = datetime.strptime(request.form['record_date'], '%Y-%m-%d')
        weather.temp_low = float(request.form['temp_low']) if request.form.get('temp_low') else None
        weather.rainfall = float(request.form['rainfall']) if request.form.get('rainfall') else None
        weather.humidity = float(request.form['humidity']) if request.form.get('humidity') else None
        weather.wind_speed = float(request.form['wind_speed']) if request.form.get('wind_speed') else None
        db.session.commit()
        flash('Weather record updated successfully!', 'success')
        return redirect(url_for('weather_list'))
    return render_template('weather/update.html', weather=weather)

@app.route('/weather/delete/<int:id>', methods=['GET', 'POST'])
def weather_delete(id):
    weather = Weather.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(weather)
        db.session.commit()
        flash('Weather record deleted successfully!', 'success')
        return redirect(url_for('weather_list'))
    return render_template('weather/delete.html', weather=weather)

# Marketing Campaigns Routes
@app.route('/marketing')
def marketing_list():
    campaigns_data = MarketingCampaigns.query.all()
    return render_template('marketing/list.html', campaigns=campaigns_data)

@app.route('/marketing/create', methods=['GET', 'POST'])
def marketing_create():
    if request.method == 'POST':
        new_campaign = MarketingCampaigns(
            campaign_name=request.form['campaign_name'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d'),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form.get('end_date') else None,
            budget=float(request.form['budget']) if request.form.get('budget') else None,
            target_audience=request.form.get('target_audience', ''),
            status=request.form['status']
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Marketing campaign added successfully!', 'success')
        return redirect(url_for('marketing_list'))
    return render_template('marketing/create.html')

@app.route('/marketing/search')
def marketing_search():
    query = request.args.get('q', '')
    if query:
        results = MarketingCampaigns.query.filter(
            MarketingCampaigns.campaign_name.contains(query) |
            MarketingCampaigns.status.contains(query)
        ).all()
    else:
        results = []
    return render_template('marketing/search.html', results=results, query=query)

@app.route('/marketing/update/<int:id>', methods=['GET', 'POST'])
def marketing_update(id):
    campaign = MarketingCampaigns.query.get_or_404(id)
    if request.method == 'POST':
        campaign.campaign_name = request.form['campaign_name']
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form.get('end_date') else None
        campaign.budget = float(request.form['budget']) if request.form.get('budget') else None
        campaign.target_audience = request.form.get('target_audience', '')
        campaign.status = request.form['status']
        db.session.commit()
        flash('Marketing campaign updated successfully!', 'success')
        return redirect(url_for('marketing_list'))
    return render_template('marketing/update.html', campaign=campaign)

@app.route('/marketing/delete/<int:id>', methods=['GET', 'POST'])
def marketing_delete(id):
    campaign = MarketingCampaigns.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(campaign)
        db.session.commit()
        flash('Marketing campaign deleted successfully!', 'success')
        return redirect(url_for('marketing_list'))
    return render_template('marketing/delete.html', campaign=campaign)

# Transportation Routes
@app.route('/transportation')
def transportation_list():
    transportation_data = Transportation.query.all()
    return render_template('transportation/list.html', transportation=transportation_data)

@app.route('/transportation/create', methods=['GET', 'POST'])
def transportation_create():
    if request.method == 'POST':
        new_transport = Transportation(
            vehicle_id=request.form['vehicle_id'],
            driver_name=request.form['driver_name'],
            route=request.form['route'],
            depart_date=datetime.strptime(request.form['depart_date'], '%Y-%m-%dT%H:%M'),
            arrive_date=datetime.strptime(request.form['arrive_date'], '%Y-%m-%dT%H:%M') if request.form.get('arrive_date') else None,
            cargo_date=datetime.strptime(request.form['cargo_date'], '%Y-%m-%d') if request.form.get('cargo_date') else None,
            status=request.form['status']
        )
        db.session.add(new_transport)
        db.session.commit()
        flash('Transportation record added successfully!', 'success')
        return redirect(url_for('transportation_list'))
    return render_template('transportation/create.html')

@app.route('/transportation/search')
def transportation_search():
    query = request.args.get('q', '')
    if query:
        results = Transportation.query.filter(
            Transportation.driver_name.contains(query) |
            Transportation.vehicle_id.contains(query) |
            Transportation.route.contains(query)
        ).all()
    else:
        results = []
    return render_template('transportation/search.html', results=results, query=query)

@app.route('/transportation/update/<int:id>', methods=['GET', 'POST'])
def transportation_update(id):
    transport = Transportation.query.get_or_404(id)
    if request.method == 'POST':
        transport.vehicle_id = request.form['vehicle_id']
        transport.driver_name = request.form['driver_name']
        transport.route = request.form['route']
        transport.depart_date = datetime.strptime(request.form['depart_date'], '%Y-%m-%dT%H:%M')
        transport.arrive_date = datetime.strptime(request.form['arrive_date'], '%Y-%m-%dT%H:%M') if request.form.get('arrive_date') else None
        transport.cargo_date = datetime.strptime(request.form['cargo_date'], '%Y-%m-%d') if request.form.get('cargo_date') else None
        transport.status = request.form['status']
        db.session.commit()
        flash('Transportation record updated successfully!', 'success')
        return redirect(url_for('transportation_list'))
    return render_template('transportation/update.html', transportation=transport)

@app.route('/transportation/delete/<int:id>', methods=['GET', 'POST'])
def transportation_delete(id):
    transport = Transportation.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(transport)
        db.session.commit()
        flash('Transportation record deleted successfully!', 'success')
        return redirect(url_for('transportation_list'))
    return render_template('transportation/delete.html', transportation=transport)

# Yield Routes
@app.route('/yield')
def yield_list():
    yield_data = Yield.query.all()
    return render_template('yield/list.html', yield_data=yield_data)

@app.route('/yield/create', methods=['GET', 'POST'])
def yield_create():
    if request.method == 'POST':
        new_yield = Yield(
            crop_id=int(request.form['crop_id']),
            estimated_yield=float(request.form['estimated_yield']),
            estimated_date=datetime.strptime(request.form['estimated_date'], '%Y-%m-%d'),
            actual_yield=float(request.form['actual_yield']) if request.form.get('actual_yield') else None,
            variance=float(request.form['variance']) if request.form.get('variance') else None
        )
        db.session.add(new_yield)
        db.session.commit()
        flash('Yield estimate added successfully!', 'success')
        return redirect(url_for('yield_list'))
    return render_template('yield/create.html')

@app.route('/yield/search')
def yield_search():
    query = request.args.get('q', '')
    if query:
        try:
            crop_id = int(query)
            results = Yield.query.filter(Yield.crop_id == crop_id).all()
        except ValueError:
            results = []
    else:
        results = []
    return render_template('yield/search.html', results=results, query=query)

@app.route('/yield/update/<int:id>', methods=['GET', 'POST'])
def yield_update(id):
    yield_record = Yield.query.get_or_404(id)
    if request.method == 'POST':
        yield_record.crop_id = int(request.form['crop_id'])
        yield_record.estimated_yield = float(request.form['estimated_yield'])
        yield_record.estimated_date = datetime.strptime(request.form['estimated_date'], '%Y-%m-%d')
        yield_record.actual_yield = float(request.form['actual_yield']) if request.form.get('actual_yield') else None
        yield_record.variance = float(request.form['variance']) if request.form.get('variance') else None
        db.session.commit()
        flash('Yield estimate updated successfully!', 'success')
        return redirect(url_for('yield_list'))
    return render_template('yield/update.html', yield_data=yield_record)  # Changed 'yield' to 'yield_data'

@app.route('/yield/delete/<int:id>', methods=['GET', 'POST'])
def yield_delete(id):
    yield_record = Yield.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(yield_record)
        db.session.commit()
        flash('Yield estimate deleted successfully!', 'success')
        return redirect(url_for('yield_list'))
    return render_template('yield/delete.html', yield_data=yield_record)  # Changed 'yield' to 'yield_data'

# User Management Routes (Basic)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if Users.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return redirect(url_for('register'))
        
        if Users.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('register'))
        
        new_user = Users(
            username=username,
            email=email,
            password=password  # In production, hash this password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create a default admin user if none exists
        if not Users.query.filter_by(username='admin').first():
            admin_user = Users(
                username='admin',
                email='admin@skyacres.com',
                password='admin123'  # Change this in production!
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: admin / admin123")
    
    app.run(debug=True)