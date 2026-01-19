# =====================================================
# HOSPITAL MANAGEMENT SYSTEM - FLASK APPLICATION
# =====================================================
# Main application file
# Run this with: python app.py

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os

# Import configuration
from config import DATABASE_URL, SECRET_KEY

# =====================================================
# APP SETUP
# =====================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# =====================================================
# DATABASE MODELS
# =====================================================

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='staff')
    full_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Department(db.Model):
    """Department/Ward model"""
    __tablename__ = 'departments'
    
    dept_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    bed_charge_per_day = db.Column(db.Numeric(10, 2), default=0)
    total_beds = db.Column(db.Integer, default=0)
    
    # Relationships
    beds = db.relationship('Bed', backref='department', lazy=True)


class Disease(db.Model):
    """Disease model"""
    __tablename__ = 'diseases'
    
    disease_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    treatment_cost = db.Column(db.Numeric(10, 2), default=0)
    avg_stay_days = db.Column(db.Integer, default=1)
    severity = db.Column(db.String(20))


class Doctor(db.Model):
    """Doctor model"""
    __tablename__ = 'doctors'
    
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(1))
    specialization = db.Column(db.String(100))
    qualification = db.Column(db.String(100))
    experience_years = db.Column(db.Integer, default=0)
    contact = db.Column(db.String(20))
    email = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationships
    assignments = db.relationship('DoctorAssignment', backref='doctor', lazy=True)
    admissions = db.relationship('Admission', backref='doctor', lazy=True)


class DoctorAssignment(db.Model):
    """Doctor ward assignment model"""
    __tablename__ = 'doctor_assignments'
    
    assignment_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'))
    shift = db.Column(db.String(20))
    duty_start_time = db.Column(db.Time)
    duty_end_time = db.Column(db.Time)
    assigned_date = db.Column(db.Date)
    duties = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Active')
    
    # Relationships
    department = db.relationship('Department', backref='assignments')


class Patient(db.Model):
    """Patient model"""
    __tablename__ = 'patients'
    
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    contact = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    blood_group = db.Column(db.String(5))
    emergency_contact = db.Column(db.String(20))
    registered_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Relationships
    admissions = db.relationship('Admission', backref='patient', lazy=True)
    bills = db.relationship('Bill', backref='patient', lazy=True)


class Bed(db.Model):
    """Bed model"""
    __tablename__ = 'beds'
    
    bed_id = db.Column(db.Integer, primary_key=True)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'))
    bed_number = db.Column(db.String(20))
    is_occupied = db.Column(db.Boolean, default=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))


class Admission(db.Model):
    """Admission model"""
    __tablename__ = 'admissions'
    
    admission_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    disease_id = db.Column(db.Integer, db.ForeignKey('diseases.disease_id'))
    bed_id = db.Column(db.Integer, db.ForeignKey('beds.bed_id'))
    admit_date = db.Column(db.Date, nullable=False)
    discharge_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Admitted')
    notes = db.Column(db.Text)
    
    # Relationships
    disease = db.relationship('Disease', backref='admissions')
    bed = db.relationship('Bed', backref='admissions')


class Bill(db.Model):
    """Bill model"""
    __tablename__ = 'bills'
    
    bill_id = db.Column(db.Integer, primary_key=True)
    admission_id = db.Column(db.Integer, db.ForeignKey('admissions.admission_id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    stay_days = db.Column(db.Integer)
    bed_charges = db.Column(db.Numeric(10, 2), default=0)
    treatment_cost = db.Column(db.Numeric(10, 2), default=0)
    doctor_fees = db.Column(db.Numeric(10, 2), default=0)
    other_charges = db.Column(db.Numeric(10, 2), default=0)
    total_amount = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(db.String(20), default='Pending')
    bill_date = db.Column(db.Date, default=datetime.utcnow)
    
    # Relationships
    admission = db.relationship('Admission', backref='bill')


class Alert(db.Model):
    """Alert model for notifications"""
    __tablename__ = 'alerts'
    
    alert_id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(50))
    message = db.Column(db.Text)
    severity = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'))


# =====================================================
# LOGIN MANAGER
# =====================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =====================================================
# ROLE-BASED ACCESS CONTROL
# =====================================================
# Roles: admin, receptionist, nurse, billing, doctor

# Define role permissions
ROLE_PERMISSIONS = {
    'admin': {
        'pages': ['dashboard', 'patients', 'doctors', 'doctor_schedule', 'beds', 'admissions', 'billing', 'analytics', 'users'],
        'actions': ['view', 'add', 'edit', 'delete', 'manage_users', 'view_revenue']
    },
    'receptionist': {
        'pages': ['dashboard', 'patients', 'beds', 'admissions'],
        'actions': ['view', 'add', 'edit']
    },
    'nurse': {
        'pages': ['dashboard', 'patients', 'beds', 'admissions'],
        'actions': ['view', 'edit']
    },
    'billing': {
        'pages': ['dashboard', 'patients', 'billing'],
        'actions': ['view', 'add', 'edit']
    },
    'doctor': {
        'pages': ['dashboard', 'patients', 'doctor_schedule', 'admissions'],
        'actions': ['view', 'edit']
    }
}

def get_user_permissions():
    """Get current user's permissions"""
    if not current_user.is_authenticated:
        return {'pages': [], 'actions': []}
    role = current_user.role or 'receptionist'
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS['receptionist'])

def can_access_page(page_name):
    """Check if user can access a page"""
    perms = get_user_permissions()
    return page_name in perms['pages']

def can_perform_action(action):
    """Check if user can perform an action"""
    perms = get_user_permissions()
    return action in perms['actions']

# Role decorators
def admin_required(f):
    """Decorator: Admin only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required!', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    """Decorator: Multiple roles allowed"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles and current_user.role != 'admin':
                flash(f'Access denied. Required role: {", ".join(roles)}', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def page_access_required(page_name):
    """Decorator: Check page access based on role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if not can_access_page(page_name):
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Context processor to make permissions available in templates
@app.context_processor
def inject_permissions():
    """Make role and permissions available in all templates"""
    try:
        if current_user.is_authenticated:
            return {
                'user_role': current_user.role,
                'user_permissions': get_user_permissions(),
                'can_access': can_access_page,
                'can_action': can_perform_action,
                'is_admin': current_user.role == 'admin'
            }
        return {
            'user_role': None,
            'user_permissions': {'pages': [], 'actions': []},
            'can_access': lambda x: False,
            'can_action': lambda x: False,
            'is_admin': False
        }
    except Exception as e:
        import sys
        import traceback
        print(f"ERROR in inject_permissions: {e}", file=sys.stderr)
        traceback.print_exc()
        # Return safe defaults
        return {
            'user_role': None,
            'user_permissions': {'pages': [], 'actions': []},
            'can_access': lambda x: False,
            'can_action': lambda x: False,
            'is_admin': False
        }


# =====================================================
# ROUTES - AUTHENTICATION
# =====================================================

@app.before_request
def log_request():
    import sys
    print(f"REQUEST: {request.method} {request.path}", file=sys.stderr)

@app.route('/')
def index():
    """Home page - redirect to login or dashboard"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            import sys
            print(f"DEBUG: Login successful for {user.username}", file=sys.stderr)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        
        # Password validation
        import re
        if len(password) < 8:
            flash('Password must be at least 8 characters long!', 'error')
            return redirect(url_for('signup'))
        
        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter (A-Z)!', 'error')
            return redirect(url_for('signup'))
        
        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter (a-z)!', 'error')
            return redirect(url_for('signup'))
        
        if not re.search(r'[0-9]', password):
            flash('Password must contain at least one number (0-9)!', 'error')
            return redirect(url_for('signup'))
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\/`~]', password):
            flash('Password must contain at least one special symbol (!@#$%^&* etc.)!', 'error')
            return redirect(url_for('signup'))
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            role='staff'  # Default role
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


# =====================================================
# ROUTES - DASHBOARD
# =====================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    try:
        # Get statistics
        stats = {
            'total_patients': Patient.query.count(),
            'admitted_patients': Admission.query.filter_by(status='Admitted').count(),
            'available_beds': Bed.query.filter_by(is_occupied=False).count(),
            'total_beds': Bed.query.count(),
            'available_doctors': Doctor.query.filter_by(is_available=True).count(),
            'total_doctors': Doctor.query.count(),
            'pending_bills': Bill.query.filter_by(status='Pending').count(),
            'total_revenue': db.session.query(db.func.sum(Bill.total_amount)).filter(
                Bill.status == 'Paid'
            ).scalar() or 0
        }
        
        # Recent admissions
        recent_admissions = Admission.query.order_by(Admission.admit_date.desc()).limit(5).all()
        
        # Get alerts
        alerts = Alert.query.filter_by(is_read=False).order_by(Alert.created_at.desc()).limit(5).all()
        
        # Check for critical conditions and create alerts
        check_and_create_alerts()
        
        print(f"DEBUG: Rendering dashboard for User: {current_user.username}, Role: {current_user.role}")
        return render_template('dashboard.html', stats=stats, recent_admissions=recent_admissions, alerts=alerts)
    except Exception as e:
        import sys
        import traceback
        import os
        
        # Write to error.log
        error_file = os.path.join(os.getcwd(), "error.log")
        with open(error_file, "w") as f:
            f.write(f"Error in dashboard: {str(e)}\n")
            traceback.print_exc(file=f)
            
        print(f"ERROR rendering dashboard: {e}", file=sys.stderr)
        traceback.print_exc()
        return f"Internal Error: {e}. Check error.log for details.", 500


def check_and_create_alerts():
    """Check conditions and create alerts"""
    # Check each department for low beds
    departments = Department.query.all()
    
    for dept in departments:
        occupied = Bed.query.filter_by(dept_id=dept.dept_id, is_occupied=True).count()
        total = dept.total_beds or 1
        occupancy = (occupied / total) * 100
        
        if occupancy >= 100:
            # No beds available
            existing = Alert.query.filter_by(
                alert_type='No Beds',
                dept_id=dept.dept_id,
                is_read=False
            ).first()
            
            if not existing:
                alert = Alert(
                    alert_type='No Beds',
                    message=f'{dept.name} has no beds available!',
                    severity='Critical',
                    dept_id=dept.dept_id
                )
                db.session.add(alert)
        
        elif occupancy >= 80:
            # Low beds warning
            existing = Alert.query.filter_by(
                alert_type='Low Beds',
                dept_id=dept.dept_id,
                is_read=False
            ).first()
            
            if not existing:
                alert = Alert(
                    alert_type='Low Beds',
                    message=f'{dept.name} has only {total - occupied} beds left!',
                    severity='Warning',
                    dept_id=dept.dept_id
                )
                db.session.add(alert)
    
    # Check for patient rush (10+ admissions today)
    today_admissions = Admission.query.filter(
        Admission.admit_date == datetime.today().date()
    ).count()
    
    if today_admissions >= 10:
        existing = Alert.query.filter_by(
            alert_type='Patient Rush',
            is_read=False
        ).filter(
            Alert.created_at >= datetime.today()
        ).first()
        
        if not existing:
            alert = Alert(
                alert_type='Patient Rush',
                message=f'High patient rush today: {today_admissions} new admissions!',
                severity='Warning'
            )
            db.session.add(alert)
    
    db.session.commit()


# =====================================================
# ROUTES - PATIENTS
# =====================================================

@app.route('/patients')
@login_required
def patients():
    """Patients list"""
    all_patients = Patient.query.order_by(Patient.patient_id.desc()).all()
    return render_template('patients.html', patients=all_patients)


@app.route('/api/patients', methods=['GET'])
@login_required
def get_patients():
    """API: Get all patients"""
    patients = Patient.query.all()
    return jsonify([{
        'patient_id': p.patient_id,
        'name': p.name,
        'age': p.age,
        'gender': p.gender,
        'contact': p.contact,
        'city': p.city,
        'blood_group': p.blood_group
    } for p in patients])


@app.route('/api/patients', methods=['POST'])
@login_required
def add_patient():
    """API: Add new patient"""
    data = request.json
    
    new_patient = Patient(
        name=data.get('name'),
        age=data.get('age'),
        gender=data.get('gender'),
        contact=data.get('contact'),
        email=data.get('email'),
        address=data.get('address'),
        city=data.get('city'),
        blood_group=data.get('blood_group'),
        emergency_contact=data.get('emergency_contact')
    )
    
    db.session.add(new_patient)
    db.session.commit()
    
    return jsonify({'success': True, 'patient_id': new_patient.patient_id})


@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
@login_required
def update_patient(patient_id):
    """API: Update patient"""
    patient = Patient.query.get_or_404(patient_id)
    data = request.json
    
    patient.name = data.get('name', patient.name)
    patient.age = data.get('age', patient.age)
    patient.gender = data.get('gender', patient.gender)
    patient.contact = data.get('contact', patient.contact)
    patient.email = data.get('email', patient.email)
    patient.address = data.get('address', patient.address)
    patient.city = data.get('city', patient.city)
    patient.blood_group = data.get('blood_group', patient.blood_group)
    patient.emergency_contact = data.get('emergency_contact', patient.emergency_contact)
    
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/patients/<int:patient_id>', methods=['DELETE'])
@login_required
def delete_patient(patient_id):
    """API: Delete patient"""
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    
    return jsonify({'success': True})


# =====================================================
# ROUTES - DOCTORS
# =====================================================

@app.route('/doctors')
@login_required
def doctors():
    """Doctors list"""
    all_doctors = Doctor.query.order_by(Doctor.doctor_id).all()
    departments = Department.query.all()
    return render_template('doctors.html', doctors=all_doctors, departments=departments)


@app.route('/api/doctors', methods=['GET'])
@login_required
def get_doctors():
    """API: Get all doctors"""
    doctors = Doctor.query.all()
    return jsonify([{
        'doctor_id': d.doctor_id,
        'name': d.name,
        'specialization': d.specialization,
        'qualification': d.qualification,
        'experience_years': d.experience_years,
        'is_available': d.is_available,
        'contact': d.contact
    } for d in doctors])


@app.route('/api/doctors', methods=['POST'])
@login_required
def add_doctor():
    """API: Add new doctor"""
    data = request.json
    
    new_doctor = Doctor(
        name=data.get('name'),
        gender=data.get('gender'),
        specialization=data.get('specialization'),
        qualification=data.get('qualification'),
        experience_years=data.get('experience_years', 0),
        contact=data.get('contact'),
        email=data.get('email'),
        is_available=data.get('is_available', True)
    )
    
    db.session.add(new_doctor)
    db.session.commit()
    
    return jsonify({'success': True, 'doctor_id': new_doctor.doctor_id})


@app.route('/api/doctors/<int:doctor_id>', methods=['PUT'])
@login_required
def update_doctor(doctor_id):
    """API: Update doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.json
    
    doctor.name = data.get('name', doctor.name)
    doctor.gender = data.get('gender', doctor.gender)
    doctor.specialization = data.get('specialization', doctor.specialization)
    doctor.qualification = data.get('qualification', doctor.qualification)
    doctor.experience_years = data.get('experience_years', doctor.experience_years)
    doctor.contact = data.get('contact', doctor.contact)
    doctor.email = data.get('email', doctor.email)
    doctor.is_available = data.get('is_available', doctor.is_available)
    
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/doctors/<int:doctor_id>', methods=['DELETE'])
@login_required
def delete_doctor(doctor_id):
    """API: Delete doctor"""
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    
    return jsonify({'success': True})


# =====================================================
# ROUTES - DOCTOR ASSIGNMENTS
# =====================================================

@app.route('/doctor-schedule')
@login_required
def doctor_schedule():
    """Doctor schedule/assignments"""
    assignments = DoctorAssignment.query.order_by(DoctorAssignment.assigned_date.desc()).all()
    doctors = Doctor.query.all()
    departments = Department.query.all()
    return render_template('doctor_schedule.html', assignments=assignments, doctors=doctors, departments=departments)


@app.route('/api/assignments', methods=['POST'])
@login_required
def add_assignment():
    """API: Add doctor assignment"""
    data = request.json
    
    from datetime import datetime
    
    new_assignment = DoctorAssignment(
        doctor_id=data.get('doctor_id'),
        dept_id=data.get('dept_id'),
        shift=data.get('shift'),
        duty_start_time=datetime.strptime(data.get('duty_start_time'), '%H:%M').time() if data.get('duty_start_time') else None,
        duty_end_time=datetime.strptime(data.get('duty_end_time'), '%H:%M').time() if data.get('duty_end_time') else None,
        assigned_date=datetime.strptime(data.get('assigned_date'), '%Y-%m-%d').date() if data.get('assigned_date') else None,
        duties=data.get('duties'),
        status=data.get('status', 'Active')
    )
    
    db.session.add(new_assignment)
    db.session.commit()
    
    return jsonify({'success': True, 'assignment_id': new_assignment.assignment_id})


# =====================================================
# ROUTES - BEDS
# =====================================================

@app.route('/beds')
@login_required
def beds():
    """Beds management"""
    all_beds = Bed.query.all()
    departments = Department.query.all()
    return render_template('beds.html', beds=all_beds, departments=departments)


@app.route('/api/beds', methods=['GET'])
@login_required
def get_beds():
    """API: Get all beds with department info"""
    beds = Bed.query.all()
    return jsonify([{
        'bed_id': b.bed_id,
        'bed_number': b.bed_number,
        'department': b.department.name if b.department else 'Unknown',
        'is_occupied': b.is_occupied
    } for b in beds])


# =====================================================
# ROUTES - ADMISSIONS
# =====================================================

@app.route('/admissions')
@login_required
def admissions():
    """Admissions list"""
    all_admissions = Admission.query.order_by(Admission.admit_date.desc()).all()
    patients = Patient.query.all()
    doctors = Doctor.query.all()
    beds = Bed.query.filter_by(is_occupied=False).all()
    diseases = Disease.query.all()
    return render_template('admissions.html', 
                         admissions=all_admissions, 
                         patients=patients, 
                         doctors=doctors, 
                         beds=beds,
                         diseases=diseases)


@app.route('/api/admissions', methods=['POST'])
@login_required
def add_admission():
    """API: Add new admission"""
    data = request.json
    
    # Create admission
    new_admission = Admission(
        patient_id=data.get('patient_id'),
        doctor_id=data.get('doctor_id'),
        disease_id=data.get('disease_id'),
        bed_id=data.get('bed_id'),
        admit_date=datetime.strptime(data.get('admit_date'), '%Y-%m-%d').date(),
        status='Admitted',
        notes=data.get('notes')
    )
    
    # Mark bed as occupied
    bed = Bed.query.get(data.get('bed_id'))
    if bed:
        bed.is_occupied = True
        bed.patient_id = data.get('patient_id')
    
    db.session.add(new_admission)
    db.session.commit()
    
    return jsonify({'success': True, 'admission_id': new_admission.admission_id})


@app.route('/api/admissions/<int:admission_id>/discharge', methods=['POST'])
@login_required
def discharge_patient(admission_id):
    """API: Discharge patient"""
    admission = Admission.query.get_or_404(admission_id)
    
    # Update admission
    admission.status = 'Discharged'
    admission.discharge_date = datetime.today().date()
    
    # Free the bed
    if admission.bed_id:
        bed = Bed.query.get(admission.bed_id)
        if bed:
            bed.is_occupied = False
            bed.patient_id = None
    
    db.session.commit()
    
    return jsonify({'success': True})


# =====================================================
# ROUTES - BILLING
# =====================================================

@app.route('/billing')
@login_required
def billing():
    """Billing page"""
    all_bills = Bill.query.order_by(Bill.bill_date.desc()).all()
    
    # Get discharged patients without bills for bill generation
    discharged = Admission.query.filter_by(status='Discharged').all()
    unbilled = [a for a in discharged if not a.bill]
    
    return render_template('billing.html', bills=all_bills, unbilled_admissions=unbilled)


@app.route('/api/bills/generate/<int:admission_id>', methods=['POST'])
@login_required
def generate_bill(admission_id):
    """API: Generate bill for admission"""
    admission = Admission.query.get_or_404(admission_id)
    
    # Check if already billed
    if admission.bill:
        return jsonify({'success': False, 'message': 'Bill already exists'})
    
    # Calculate charges
    stay_days = 1
    if admission.discharge_date and admission.admit_date:
        stay_days = max(1, (admission.discharge_date - admission.admit_date).days)
    
    # Get bed charge
    bed_charge_per_day = 1500  # Default
    if admission.bed and admission.bed.department:
        bed_charge_per_day = float(admission.bed.department.bed_charge_per_day or 1500)
    
    bed_charges = stay_days * bed_charge_per_day
    
    # Get treatment cost
    treatment_cost = 10000  # Default
    if admission.disease:
        treatment_cost = float(admission.disease.treatment_cost or 10000)
    
    # Doctor fees and other charges
    doctor_fees = 2000
    other_charges = 500
    
    total = bed_charges + treatment_cost + doctor_fees + other_charges
    
    # Create bill
    new_bill = Bill(
        admission_id=admission_id,
        patient_id=admission.patient_id,
        stay_days=stay_days,
        bed_charges=bed_charges,
        treatment_cost=treatment_cost,
        doctor_fees=doctor_fees,
        other_charges=other_charges,
        total_amount=total,
        status='Pending',
        bill_date=datetime.today().date()
    )
    
    db.session.add(new_bill)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'bill_id': new_bill.bill_id,
        'total': float(total)
    })


@app.route('/api/bills/<int:bill_id>/pay', methods=['POST'])
@login_required
def mark_bill_paid(bill_id):
    """API: Mark bill as paid"""
    bill = Bill.query.get_or_404(bill_id)
    bill.status = 'Paid'
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/bills', methods=['GET'])
@login_required
def get_bills():
    """API: Get all bills"""
    bills = Bill.query.all()
    return jsonify([{
        'bill_id': b.bill_id,
        'patient_name': b.patient.name if b.patient else 'Unknown',
        'total_amount': float(b.total_amount),
        'status': b.status,
        'bill_date': b.bill_date.strftime('%Y-%m-%d') if b.bill_date else None
    } for b in bills])


# =====================================================
# ROUTES - ANALYTICS
# =====================================================

@app.route('/analytics')
@login_required
def analytics():
    """Analytics page"""
    return render_template('analytics.html')


@app.route('/api/analytics/overview', methods=['GET'])
@login_required
def analytics_overview():
    """API: Get analytics overview data"""
    
    # Total revenue
    total_revenue = db.session.query(db.func.sum(Bill.total_amount)).filter(
        Bill.status == 'Paid'
    ).scalar() or 0
    
    # Revenue by department
    dept_revenue = db.session.query(
        Department.name,
        db.func.sum(Bill.total_amount)
    ).join(
        Bed, Department.dept_id == Bed.dept_id
    ).join(
        Admission, Bed.bed_id == Admission.bed_id
    ).join(
        Bill, Admission.admission_id == Bill.admission_id
    ).group_by(Department.name).all()
    
    # Disease statistics
    disease_stats = db.session.query(
        Disease.name,
        db.func.count(Admission.admission_id)
    ).join(
        Admission, Disease.disease_id == Admission.disease_id
    ).group_by(Disease.name).all()
    
    # Monthly admissions - Use to_char for PostgreSQL
    monthly_admissions = db.session.query(
        db.func.to_char(Admission.admit_date, 'YYYY-MM'),
        db.func.count(Admission.admission_id)
    ).group_by(
        db.func.to_char(Admission.admit_date, 'YYYY-MM')
    ).order_by(
        db.func.to_char(Admission.admit_date, 'YYYY-MM')
    ).limit(12).all()
    
    return jsonify({
        'total_revenue': float(total_revenue),
        'department_revenue': [{'name': d[0], 'revenue': float(d[1] or 0)} for d in dept_revenue],
        'disease_stats': [{'name': d[0], 'count': d[1]} for d in disease_stats],
        'monthly_admissions': [{'month': m[0], 'count': m[1]} for m in monthly_admissions]
    })


@app.route('/api/analytics/beds', methods=['GET'])
@login_required
def analytics_beds():
    """API: Get bed occupancy data"""
    departments = Department.query.all()
    
    data = []
    for dept in departments:
        occupied = Bed.query.filter_by(dept_id=dept.dept_id, is_occupied=True).count()
        total = dept.total_beds or 0
        available = total - occupied
        
        data.append({
            'department': dept.name,
            'occupied': occupied,
            'available': available,
            'total': total,
            'occupancy_rate': round((occupied / total * 100) if total > 0 else 0, 1)
        })
    
    return jsonify(data)


@app.route('/api/analytics/doctors', methods=['GET'])
@login_required
def analytics_doctors():
    """API: Get doctor workload data"""
    doctors = Doctor.query.all()
    
    data = []
    for doc in doctors:
        patient_count = Admission.query.filter_by(
            doctor_id=doc.doctor_id,
            status='Admitted'
        ).count()
        
        data.append({
            'name': doc.name,
            'specialization': doc.specialization,
            'patients': patient_count,
            'available': doc.is_available
        })
    
    # Sort by patient count
    data.sort(key=lambda x: x['patients'], reverse=True)
    
    return jsonify(data[:10])  # Top 10


@app.route('/api/analytics/seasonal-diseases', methods=['GET'])
@login_required
def analytics_seasonal_diseases():
    """API: Get disease distribution by season"""
    # Define seasons based on Indian climate
    # Winter: Dec, Jan, Feb | Spring: Mar, Apr | Summer: May, Jun
    # Monsoon: Jul, Aug, Sep | Autumn: Oct, Nov
    
    def get_season(month):
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4]:
            return 'Spring'
        elif month in [5, 6]:
            return 'Summer'
        elif month in [7, 8, 9]:
            return 'Monsoon'
        else:  # 10, 11
            return 'Autumn'
    
    # Get all admissions with disease info
    admissions = db.session.query(
        Admission.admit_date,
        Disease.name
    ).join(
        Disease, Admission.disease_id == Disease.disease_id
    ).filter(
        Admission.admit_date.isnot(None)
    ).all()
    
    # Group by season and disease
    season_data = {}
    for admit_date, disease_name in admissions:
        season = get_season(admit_date.month)
        
        if season not in season_data:
            season_data[season] = {}
        
        if disease_name not in season_data[season]:
            season_data[season][disease_name] = 0
        
        season_data[season][disease_name] += 1
    
    # Format response - top 5 diseases per season
    result = []
    season_order = ['Winter', 'Spring', 'Summer', 'Monsoon', 'Autumn']
    
    for season in season_order:
        if season in season_data:
            diseases = [
                {'name': name, 'count': count}
                for name, count in season_data[season].items()
            ]
            # Sort by count descending, take top 5
            diseases.sort(key=lambda x: x['count'], reverse=True)
            result.append({
                'season': season,
                'diseases': diseases[:5]
            })
    
    return jsonify(result)


# =====================================================
# ROUTES - ALERTS
# =====================================================

@app.route('/api/alerts', methods=['GET'])
@login_required
def get_alerts():
    """API: Get unread alerts"""
    alerts = Alert.query.filter_by(is_read=False).order_by(Alert.created_at.desc()).all()
    
    return jsonify([{
        'alert_id': a.alert_id,
        'type': a.alert_type,
        'message': a.message,
        'severity': a.severity,
        'created_at': a.created_at.strftime('%Y-%m-%d %H:%M') if a.created_at else None
    } for a in alerts])


@app.route('/api/alerts/<int:alert_id>/read', methods=['POST'])
@login_required
def mark_alert_read(alert_id):
    """API: Mark alert as read"""
    alert = Alert.query.get_or_404(alert_id)
    alert.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})


# =====================================================
# ROUTES - USER MANAGEMENT (Admin Only)
# =====================================================

@app.route('/users')
@login_required
@admin_required
def manage_users():
    """User management page - Admin only"""
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=all_users)


@app.route('/api/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """API: Get all users"""
    users = User.query.all()
    return jsonify([{
        'user_id': u.user_id,
        'username': u.username,
        'email': u.email,
        'full_name': u.full_name,
        'role': u.role,
        'created_at': u.created_at.strftime('%Y-%m-%d') if u.created_at else None,
        'last_login': u.last_login.strftime('%Y-%m-%d %H:%M') if u.last_login else 'Never'
    } for u in users])


@app.route('/api/users', methods=['POST'])
@login_required
@admin_required
def add_user():
    """API: Add new user (Admin only)"""
    data = request.json
    
    # Check if user exists
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'success': False, 'message': 'Email already exists'})
    
    new_user = User(
        username=data.get('username'),
        email=data.get('email'),
        full_name=data.get('full_name'),
        role=data.get('role', 'receptionist')
    )
    new_user.set_password(data.get('password', 'Hospital@123'))
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'success': True, 'user_id': new_user.user_id})


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """API: Update user"""
    user = User.query.get_or_404(user_id)
    data = request.json
    
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.role = data.get('role', user.role)
    
    # Update password if provided
    if data.get('password'):
        user.set_password(data.get('password'))
    
    db.session.commit()
    
    return jsonify({'success': True})


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """API: Delete user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the current admin
    if user.user_id == current_user.user_id:
        return jsonify({'success': False, 'message': 'Cannot delete your own account'})
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True})


# =====================================================
# DATABASE INITIALIZATION ROUTE (For Production Setup)
# =====================================================

@app.route('/initialize-db-secret-route-2024')
def initialize_database_route():
    """Initialize database via web - ONE TIME USE ONLY"""
    try:
        # Check if already initialized
        if User.query.first():
            return "Database already initialized! Please go to <a href='/login'>/login</a>"
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@hospital.com',
            full_name='System Administrator',
            role='admin'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        
        # Create other users
        users_data = [
            ('receptionist1', 'receptionist@hospital.com', 'John Receptionist', 'receptionist'),
            ('nurse1', 'nurse@hospital.com', 'Mary Nurse', 'nurse'),
            ('billing1', 'billing@hospital.com', 'Robert Billing', 'billing'),
            ('doctor1', 'doctor@hospital.com', 'Dr. Sarah Doctor', 'doctor'),
        ]
        
        for username, email, full_name, role in users_data:
            user = User(username=username, email=email, full_name=full_name, role=role)
            user.set_password('Hospital@123')
            db.session.add(user)
        
        # Create departments
        departments_data = [
            {'name': 'ICU', 'type': 'Critical Care', 'bed_charge_per_day': 5000, 'total_beds': 10},
            {'name': 'General Ward', 'type': 'General', 'bed_charge_per_day': 2000, 'total_beds': 50},
            {'name': 'Emergency', 'type': 'Emergency', 'bed_charge_per_day': 3000, 'total_beds': 20},
            {'name': 'Surgery Ward', 'type': 'Surgical', 'bed_charge_per_day': 4000, 'total_beds': 30},
            {'name': 'Cardiac Care', 'type': 'Specialized', 'bed_charge_per_day': 6000, 'total_beds': 15},
        ]
        
        departments = []
        for dept_data in departments_data:
            dept = Department(**dept_data)
            db.session.add(dept)
            departments.append(dept)
        
        db.session.flush()
        
        # Create beds
        for dept in departments:
            prefix = dept.name[:3].upper()
            for i in range(1, dept.total_beds + 1):
                bed = Bed(
                    dept_id=dept.dept_id,
                    bed_number=f"{prefix}-{i:03d}",
                    is_occupied=False
                )
                db.session.add(bed)
        
        # Create diseases
        diseases_data = [
            {'name': 'Pneumonia', 'treatment_cost': 25000, 'avg_stay_days': 7, 'severity': 'Moderate'},
            {'name': 'Heart Attack', 'treatment_cost': 150000, 'avg_stay_days': 10, 'severity': 'Critical'},
            {'name': 'Diabetes', 'treatment_cost': 15000, 'avg_stay_days': 3, 'severity': 'Mild'},
            {'name': 'Fracture', 'treatment_cost': 35000, 'avg_stay_days': 5, 'severity': 'Moderate'},
            {'name': 'Appendicitis', 'treatment_cost': 45000, 'avg_stay_days': 4, 'severity': 'Moderate'},
        ]
        
        for disease_data in diseases_data:
            disease = Disease(**disease_data)
            db.session.add(disease)
        
        # Create doctors
        doctors_data = [
            {'name': 'Dr. Rajesh Kumar', 'gender': 'M', 'specialization': 'Cardiology', 
             'qualification': 'MBBS, MD', 'experience_years': 15, 'contact': '9876543210', 
             'email': 'rajesh@hospital.com', 'is_available': True},
            {'name': 'Dr. Priya Sharma', 'gender': 'F', 'specialization': 'Pediatrics', 
             'qualification': 'MBBS, DCH', 'experience_years': 10, 'contact': '9876543211', 
             'email': 'priya@hospital.com', 'is_available': True},
            {'name': 'Dr. Amit Patel', 'gender': 'M', 'specialization': 'Orthopedics', 
             'qualification': 'MBBS, MS', 'experience_years': 12, 'contact': '9876543212', 
             'email': 'amit@hospital.com', 'is_available': True},
        ]
        
        for doctor_data in doctors_data:
            doctor = Doctor(**doctor_data)
            db.session.add(doctor)
        
        db.session.commit()
        
        return """
        <h1>✅ Database Initialized Successfully!</h1>
        <p>Your hospital management system is ready to use.</p>
        <h2>Login Credentials:</h2>
        <ul>
            <li><strong>Admin:</strong> admin / Admin@123</li>
            <li><strong>Receptionist:</strong> receptionist1 / Hospital@123</li>
            <li><strong>Nurse:</strong> nurse1 / Hospital@123</li>
            <li><strong>Billing:</strong> billing1 / Hospital@123</li>
            <li><strong>Doctor:</strong> doctor1 / Hospital@123</li>
        </ul>
        <p><a href="/login" style="font-size: 20px; color: #00796B;">Go to Login Page →</a></p>
        """
        
    except Exception as e:
        import traceback
        return f"<h1>Error initializing database:</h1><pre>{str(e)}\n\n{traceback.format_exc()}</pre>"


# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    # Create tables if not exist
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@hospital.com',
                full_name='Smit',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Created default admin user: admin / admin123")
    
    # Run the app
    print("Starting Hospital Management System...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
