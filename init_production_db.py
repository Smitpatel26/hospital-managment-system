#!/usr/bin/env python3
"""
Database Initialization Script for Production
Run this after deploying to Render to set up the database
"""

from app import app, db, User, Department, Disease, Doctor, Patient, Bed, Admission, Bill, DoctorAssignment
from datetime import datetime, date, time
import random

def init_production_database():
    """Initialize database with essential data for production"""
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Check if data already exists
        if User.query.first():
            print("Database already initialized!")
            return
        
        print("Adding initial data...")
        
        # 1. Create Admin User
        admin = User(
            username='admin',
            email='admin@hospital.com',
            full_name='System Administrator',
            role='admin'
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        
        # 2. Create Sample Users for Different Roles
        receptionist = User(username='receptionist1', email='receptionist@hospital.com', 
                          full_name='John Receptionist', role='receptionist')
        receptionist.set_password('Hospital@123')
        db.session.add(receptionist)
        
        nurse = User(username='nurse1', email='nurse@hospital.com', 
                    full_name='Mary Nurse', role='nurse')
        nurse.set_password('Hospital@123')
        db.session.add(nurse)
        
        billing = User(username='billing1', email='billing@hospital.com', 
                      full_name='Robert Billing', role='billing')
        billing.set_password('Hospital@123')
        db.session.add(billing)
        
        doctor_user = User(username='doctor1', email='doctor@hospital.com', 
                          full_name='Dr. Sarah Doctor', role='doctor')
        doctor_user.set_password('Hospital@123')
        db.session.add(doctor_user)
        
        # 3. Create Departments
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
        
        db.session.flush()  # Get department IDs
        
        # 4. Create Beds
        bed_counter = 1
        for dept in departments:
            prefix = dept.name[:3].upper()
            for i in range(1, dept.total_beds + 1):
                bed = Bed(
                    dept_id=dept.dept_id,
                    bed_number=f"{prefix}-{i:03d}",
                    is_occupied=False
                )
                db.session.add(bed)
        
        # 5. Create Diseases
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
        
        # 6. Create Doctors
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
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print("\n" + "="*50)
        print("LOGIN CREDENTIALS:")
        print("="*50)
        print("Admin:")
        print("  Username: admin")
        print("  Password: Admin@123")
        print("\nOther roles:")
        print("  receptionist1 / Hospital@123")
        print("  nurse1 / Hospital@123")
        print("  billing1 / Hospital@123")
        print("  doctor1 / Hospital@123")
        print("="*50)

if __name__ == '__main__':
    init_production_database()
