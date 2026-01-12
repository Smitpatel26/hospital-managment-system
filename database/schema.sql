-- =====================================================
-- HOSPITAL MANAGEMENT SYSTEM - DATABASE SCHEMA
-- =====================================================
-- This file creates all tables for the hospital system
-- Run this in PostgreSQL to set up the database

-- Create Database (run separately if needed)
-- CREATE DATABASE hospital_db;

-- =====================================================
-- TABLE 1: USERS (Authentication)
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff',  -- 'admin' or 'staff'
    full_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- =====================================================
-- TABLE 2: DEPARTMENTS / WARDS
-- =====================================================
CREATE TABLE IF NOT EXISTS departments (
    dept_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),  -- Critical Care, General, Emergency, etc.
    bed_charge_per_day DECIMAL(10, 2) DEFAULT 0,
    total_beds INTEGER DEFAULT 0
);

-- =====================================================
-- TABLE 3: DISEASES
-- =====================================================
CREATE TABLE IF NOT EXISTS diseases (
    disease_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    treatment_cost DECIMAL(10, 2) DEFAULT 0,
    avg_stay_days INTEGER DEFAULT 1,
    severity VARCHAR(20)  -- Mild, Moderate, Severe, Critical
);

-- =====================================================
-- TABLE 4: DOCTORS
-- =====================================================
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    gender CHAR(1),
    specialization VARCHAR(100),
    qualification VARCHAR(100),
    experience_years INTEGER DEFAULT 0,
    contact VARCHAR(20),
    email VARCHAR(100),
    is_available BOOLEAN DEFAULT TRUE
);

-- =====================================================
-- TABLE 5: DOCTOR ASSIGNMENTS (Ward Duty)
-- =====================================================
CREATE TABLE IF NOT EXISTS doctor_assignments (
    assignment_id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(doctor_id),
    dept_id INTEGER REFERENCES departments(dept_id),
    shift VARCHAR(20),  -- Morning, Evening, Night
    duty_start_time TIME,
    duty_end_time TIME,
    assigned_date DATE,
    duties VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Active'  -- Active, On Leave
);

-- =====================================================
-- TABLE 6: PATIENTS
-- =====================================================
CREATE TABLE IF NOT EXISTS patients (
    patient_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER,
    gender CHAR(1),
    contact VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    city VARCHAR(50),
    blood_group VARCHAR(5),
    emergency_contact VARCHAR(20),
    registered_date DATE DEFAULT CURRENT_DATE
);

-- =====================================================
-- TABLE 7: BEDS
-- =====================================================
CREATE TABLE IF NOT EXISTS beds (
    bed_id SERIAL PRIMARY KEY,
    dept_id INTEGER REFERENCES departments(dept_id),
    bed_number VARCHAR(20),
    is_occupied BOOLEAN DEFAULT FALSE,
    patient_id INTEGER REFERENCES patients(patient_id)
);

-- =====================================================
-- TABLE 8: ADMISSIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS admissions (
    admission_id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(patient_id),
    doctor_id INTEGER REFERENCES doctors(doctor_id),
    disease_id INTEGER REFERENCES diseases(disease_id),
    bed_id INTEGER REFERENCES beds(bed_id),
    admit_date DATE NOT NULL,
    discharge_date DATE,
    status VARCHAR(20) DEFAULT 'Admitted',  -- Admitted, Discharged
    notes TEXT
);

-- =====================================================
-- TABLE 9: BILLS
-- =====================================================
CREATE TABLE IF NOT EXISTS bills (
    bill_id SERIAL PRIMARY KEY,
    admission_id INTEGER REFERENCES admissions(admission_id),
    patient_id INTEGER REFERENCES patients(patient_id),
    stay_days INTEGER,
    bed_charges DECIMAL(10, 2) DEFAULT 0,
    treatment_cost DECIMAL(10, 2) DEFAULT 0,
    doctor_fees DECIMAL(10, 2) DEFAULT 0,
    other_charges DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Pending',  -- Paid, Pending
    bill_date DATE DEFAULT CURRENT_DATE
);

-- =====================================================
-- TABLE 10: ALERTS (For notifications)
-- =====================================================
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),  -- No Beds, Low Beds, Patient Rush, etc.
    message TEXT,
    severity VARCHAR(20),  -- Critical, Warning, Info
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    dept_id INTEGER REFERENCES departments(dept_id)
);

-- =====================================================
-- CREATE INDEXES FOR FASTER QUERIES
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_admissions_status ON admissions(status);
CREATE INDEX IF NOT EXISTS idx_admissions_date ON admissions(admit_date);
CREATE INDEX IF NOT EXISTS idx_bills_status ON bills(status);
CREATE INDEX IF NOT EXISTS idx_beds_occupied ON beds(is_occupied);
CREATE INDEX IF NOT EXISTS idx_doctors_available ON doctors(is_available);
