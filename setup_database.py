# =====================================================
# DATABASE SETUP SCRIPT
# Creates hospital_db database and loads all data
# =====================================================

import psycopg2
from psycopg2 import sql
import csv
import os
from werkzeug.security import generate_password_hash

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'smit2609'
}

def create_database():
    """Create the hospital_db database if it doesn't exist"""
    print("Connecting to PostgreSQL...")
    
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='hospital_db'")
    if cursor.fetchone():
        print("✓ Database 'hospital_db' already exists")
    else:
        cursor.execute("CREATE DATABASE hospital_db")
        print("✓ Created database 'hospital_db'")
    
    cursor.close()
    conn.close()

def create_tables():
    """Create all tables in hospital_db"""
    print("\nCreating tables...")
    
    conn = psycopg2.connect(**DB_CONFIG, database='hospital_db')
    cursor = conn.cursor()
    
    # Read and execute schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    cursor.execute(schema_sql)
    conn.commit()
    print("✓ All tables created successfully")
    
    cursor.close()
    conn.close()

def load_csv_data(table_name, csv_file, columns):
    """Load data from CSV into table"""
    conn = psycopg2.connect(**DB_CONFIG, database='hospital_db')
    cursor = conn.cursor()
    
    csv_path = os.path.join(os.path.dirname(__file__), 'data', csv_file)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            values = []
            for col in columns:
                val = row.get(col, '')
                # Handle empty values
                if val == '' or val == 'None':
                    values.append(None)
                elif val == 'True':
                    values.append(True)
                elif val == 'False':
                    values.append(False)
                else:
                    values.append(val)
            
            placeholders = ','.join(['%s'] * len(columns))
            cols = ','.join(columns)
            
            try:
                cursor.execute(
                    f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
                    values
                )
                count += 1
            except Exception as e:
                print(f"  Error inserting row: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✓ Loaded {count} records into {table_name}")

def load_all_data():
    """Load all CSV data into database"""
    print("\nLoading data from CSV files...")
    
    # Departments
    load_csv_data('departments', 'departments.csv', 
        ['dept_id', 'name', 'type', 'bed_charge_per_day', 'total_beds'])
    
    # Diseases
    load_csv_data('diseases', 'diseases.csv',
        ['disease_id', 'name', 'treatment_cost', 'avg_stay_days', 'severity'])
    
    # Doctors
    load_csv_data('doctors', 'doctors.csv',
        ['doctor_id', 'name', 'gender', 'specialization', 'qualification', 
         'experience_years', 'contact', 'email', 'is_available'])
    
    # Patients
    load_csv_data('patients', 'patients.csv',
        ['patient_id', 'name', 'age', 'gender', 'contact', 'email', 
         'address', 'city', 'blood_group', 'emergency_contact', 'registered_date'])
    
    # Beds
    load_csv_data('beds', 'beds.csv',
        ['bed_id', 'dept_id', 'bed_number', 'is_occupied', 'patient_id'])
    
    # Doctor Assignments
    load_csv_data('doctor_assignments', 'doctor_assignments.csv',
        ['assignment_id', 'doctor_id', 'dept_id', 'shift', 
         'duty_start_time', 'duty_end_time', 'assigned_date', 'duties', 'status'])
    
    # Admissions
    load_csv_data('admissions', 'admissions.csv',
        ['admission_id', 'patient_id', 'doctor_id', 'disease_id', 'bed_id',
         'admit_date', 'discharge_date', 'status', 'notes'])
    
    # Bills
    load_csv_data('bills', 'bills.csv',
        ['bill_id', 'admission_id', 'patient_id', 'stay_days', 'bed_charges',
         'treatment_cost', 'doctor_fees', 'other_charges', 'total_amount', 'status', 'bill_date'])

def create_admin_user():
    """Create default admin user"""
    print("\nCreating admin user...")
    
    conn = psycopg2.connect(**DB_CONFIG, database='hospital_db')
    cursor = conn.cursor()
    
    # Check if admin exists
    cursor.execute("SELECT 1 FROM users WHERE username = 'admin'")
    if cursor.fetchone():
        print("✓ Admin user already exists")
    else:
        password_hash = generate_password_hash('admin123')
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (%s, %s, %s, %s, %s)
        """, ('admin', 'admin@hospital.com', password_hash, 'admin', 'Smit'))
        conn.commit()
        print("✓ Created admin user: admin / admin123")
    
    # Create staff user
    cursor.execute("SELECT 1 FROM users WHERE username = 'staff'")
    if not cursor.fetchone():
        password_hash = generate_password_hash('staff123')
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (%s, %s, %s, %s, %s)
        """, ('staff', 'staff@hospital.com', password_hash, 'staff', 'Staff User'))
        conn.commit()
        print("✓ Created staff user: staff / staff123")
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("HOSPITAL DATABASE SETUP")
    print("=" * 50)
    
    try:
        create_database()
        create_tables()
        load_all_data()
        create_admin_user()
        
        print("\n" + "=" * 50)
        print("✓ DATABASE SETUP COMPLETE!")
        print("=" * 50)
        print("\nYou can now run: python app.py")
        print("Then open: http://localhost:5000")
        print("\nLogin credentials:")
        print("  Admin: admin / admin123")
        print("  Staff: staff / staff123")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
