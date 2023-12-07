from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import pymysql
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date, timedelta
from flask_login import *
from flask_migrate import Migrate


pymysql.install_as_MySQLdb()

db_password = os.environ.get("DB_PASSWORD")
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'optional_default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:{db_password}@localhost/Project3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Silence the deprecation warning

db = SQLAlchemy(app)
migrate = Migrate(app, db)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class Tenant(db.Model, UserMixin):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=True)
    apartment_number = db.Column(db.String(20), nullable=False)
    maintenance_requests = db.relationship('MaintenanceRequest', backref='tenant', lazy=True)

    def __repr__(self):
        return f'<Tenant {self.name}>'


class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    id = db.Column(db.Integer, primary_key=True)
    # request_id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.String(200), nullable=True)  # Optional
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    apartment_number = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return self.id


class Manager(db.Model):
    __tablename__ = 'managers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)


class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Staff {self.name}>'


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/manger_tenants')
def tenants():
    tenants = Tenant.query.all()
    return render_template('index.html', tenants=tenants)


@app.route('/manager')
def manager_page():
    # Get a list of all tenants to display
    tenants = Tenant.query.all()
    return render_template('manager.html', tenants=tenants)


@app.route('/manager/add_tenant', methods=['POST'])
def add_tenant():
    # Extract form data
    id = request.form['id']
    name = request.form['name']
    phone_number = request.form['phone_number']
    email = request.form['email']
    apartment_number = request.form['apartment_number']
    check_in_date = request.form['check_in_date']

    # Create new tenant
    new_tenant = Tenant(id=id, name=name, phone_number=phone_number, email=email,
                        apartment_number=apartment_number, check_in_date=check_in_date)
    db.session.add(new_tenant)
    db.session.commit()
    flash('New tenant added.')
    return redirect(url_for('manager_page'))


@app.route('/manager/move_tenant', methods=['POST'])
def move_tenant():
    tenant_id = request.form['tenant_id']
    new_apartment_number = request.form['new_apartment_number']

    # Find tenant and update apartment number
    tenant = Tenant.query.get(tenant_id)
    if tenant:
        tenant.apartment_number = new_apartment_number
        db.session.commit()
        flash('Tenant moved to new apartment.')
    else:
        flash('Tenant not found.')
    return redirect(url_for('manager_page'))


@app.route('/manager/delete_tenant', methods=['POST'])
def delete_tenant():
    tenant_id = request.form['tenant_id']

    # Find tenant and delete
    tenant = Tenant.query.get(tenant_id)
    if tenant:
        db.session.delete(tenant)
        db.session.commit()
        flash('Tenant deleted.')
    else:
        flash('Tenant not found.')
    return redirect(url_for('manager_page'))


@app.route('/staff', methods=['GET'])
def staff_page():
    # Retrieve filter options from the query parameters
    apartment_number = request.args.get('apartment_number')
    area = request.args.get('area')
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Start with a base query
    query = MaintenanceRequest.query

    # Apply filters as necessary
    if apartment_number:
        query = query.filter_by(apartment_number=apartment_number)
    if area:
        query = query.filter_by(area=area)
    if status:
        query = query.filter_by(status=status)
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        query = query.filter(MaintenanceRequest.date_time >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        end_date += timedelta(days=1)
        query = query.filter(MaintenanceRequest.date_time <= end_date)

    # Execute the query
    maintenance_requests = query.all()

    # Render the template, passing in the maintenance requests
    return render_template('staff.html', maintenance_requests=maintenance_requests)


@app.route('/maintenance_request', methods=['GET'])
def maintenance_request_page():
    tenant_id = request.args.get('tenant_id')

    # Check if tenant_id is provided
    if not tenant_id:
        flash('Tenant ID is required.')
        return redirect(url_for('login'))

    # Convert tenant_id to integer
    try:
        tenant_id = int(tenant_id)
    except ValueError:
        flash('Invalid Tenant ID.')
        return redirect(url_for('login'))

    # Fetch maintenance requests for the specific tenant
    requests = MaintenanceRequest.query.filter_by(tenant_id=tenant_id).order_by(MaintenanceRequest.date_time.desc()).all()

    return render_template('maintenance_request.html', requests=requests, tenant_id=tenant_id)



DEFAULT_IMAGE = "No_image_available.svg.png"


@app.route('/tenant', methods=['GET', 'POST'])
def tenant_page():
    tenant_id = request.args.get('tenant_id')

    # Redirect to login if tenant_id is not provided
    if not tenant_id:
        flash('ID is required.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Extract form data
        apartment_number = request.form['apartment_number']
        problem_area = request.form['problem_area']
        description = request.form['description']

        # Handle file upload
        file = request.files.get('image')
        filename = DEFAULT_IMAGE
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Create and save the maintenance request
        new_request = MaintenanceRequest(
            apartment_number=apartment_number,
            area=problem_area,
            description=description,
            date_time=datetime.utcnow(),
            image=filename,
            tenant_id=tenant_id  # Use the provided tenant_id
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Maintenance request submitted successfully.')

    # Fetch request history for the tenant
    requests = MaintenanceRequest.query.filter_by(tenant_id=tenant_id).all()
    return render_template('tenant.html', tenant_id=tenant_id, requests=requests)

@app.route('/submit_request', methods=['POST'])
def submit_request():
    tenant_id = request.args.get('tenant_id')
    try:
        apartment_number = request.form['apartment_number']
        problem_area = request.form['problem_area']
        description = request.form['description']

        file = request.files.get('image')
        filename = DEFAULT_IMAGE
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if not tenant_id:
            flash('Tenant not found.')
            return redirect(url_for('tenant_page'))

        new_request = MaintenanceRequest(
            apartment_number=apartment_number,
            area=problem_area,
            description=description,
            image=filename,  # This will be None if no file was uploaded
            status='pending',  # Default status
            date_time=datetime.utcnow(),
            tenant_id=tenant_id
        )
        db.session.add(new_request)
        db.session.commit()
        flash('Maintenance request submitted successfully.')
    except Exception as e:
        flash('An error occurred while submitting the maintenance request.')
        app.logger.error(f'Error submitting maintenance request: {e}')

    return redirect(url_for('maintenance_request_page', tenant_id=tenant_id))


@app.route('/update_request/<int:request_id>', methods=['POST'])
def update_request(request_id):
    # Find the request
    m_request = MaintenanceRequest.query.get_or_404(request_id)

    # Update the status
    m_request.status = 'Completed'  # Assuming you're setting it as completed

    # Save the changes
    db.session.commit()

    # Redirect back to the staff page or handle via JavaScript
    return redirect(url_for('staff_page'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # In case tables haven't been created yet
    app.run(debug=True)

