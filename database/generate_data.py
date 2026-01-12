# =====================================================
# SYNTHETIC DATA GENERATOR - INDIAN NAMES
# =====================================================
# This script generates realistic hospital data with Indian names
# Run this script to create CSV files in the data folder

import csv
import random
from datetime import datetime, timedelta
import os

# =====================================================
# INDIAN DATA LISTS
# =====================================================

# Indian First Names (Male)
MALE_FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Shaurya", "Atharva", "Advik", "Pranav", "Advaith",
    "Aarush", "Kabir", "Ritvik", "Anirudh", "Dhruv", "Aryan", "Yash", "Rohan",
    "Rahul", "Amit", "Vikram", "Suresh", "Rajesh", "Mahesh", "Ganesh",
    "Karan", "Nikhil", "Akash", "Deepak", "Ravi", "Sanjay", "Vijay", "Ajay",
    "Mohan", "Gopal", "Ramesh", "Sunil", "Anil", "Manoj", "Pankaj", "Rakesh",
    "Harish", "Naresh", "Dinesh", "Mukesh", "Sachin", "Gaurav", "Varun", "Tarun"
]

# Indian First Names (Female)
FEMALE_FIRST_NAMES = [
    "Saanvi", "Aanya", "Aadhya", "Aaradhya", "Ananya", "Pari", "Anika", "Navya",
    "Diya", "Kiara", "Myra", "Sara", "Ira", "Ahana", "Anvi", "Priya",
    "Kavya", "Ishita", "Siya", "Avni", "Riya", "Pooja", "Neha", "Sneha",
    "Divya", "Shruti", "Anjali", "Sunita", "Anita", "Kavitha", "Lakshmi",
    "Meera", "Radha", "Gita", "Sita", "Rekha", "Seema", "Reena", "Meena",
    "Preeti", "Jyoti", "Swati", "Shweta", "Nisha", "Asha", "Usha", "Pushpa",
    "Kamala", "Padma", "Saroj", "Kusum", "Mala", "Lata", "Geeta", "Rita"
]

# Indian Last Names
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Shah", "Joshi",
    "Mishra", "Pandey", "Tiwari", "Shukla", "Dubey", "Srivastava", "Agarwal",
    "Jain", "Mehta", "Kapoor", "Malhotra", "Chopra", "Reddy", "Rao", "Naidu",
    "Iyer", "Nair", "Menon", "Pillai", "Krishnan", "Mukherjee", "Banerjee",
    "Chatterjee", "Bose", "Das", "Sen", "Roy", "Ghosh", "Dutta", "Patil",
    "Deshmukh", "Kulkarni", "Joshi", "Desai", "Modi", "Thakur", "Chauhan",
    "Yadav", "Rathore", "Rajput", "Saxena", "Mathur", "Awasthi", "Trivedi"
]

# Indian Cities
CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune",
    "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Bhopal",
    "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad",
    "Meerut", "Rajkot", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad",
    "Amritsar", "Allahabad", "Ranchi", "Coimbatore", "Jabalpur", "Gwalior",
    "Vijayawada", "Jodhpur", "Madurai", "Raipur", "Kota", "Chandigarh", "Guwahati"
]

# =====================================================
# DISEASES WITH REALISTIC INDIAN HOSPITAL COSTS
# =====================================================
# Pricing based on actual Indian hospital charges (Private hospitals)
# Format: (Disease Name, Treatment Cost INR, Avg Stay Days, Severity)
# Costs include: Treatment, Medicines, Diagnostics, Doctor Fees
DISEASES_DATA = [
    # Vector-borne diseases (Monsoon)
    ("Dengue Fever", 25000, 5, "Moderate"),       # Platelet monitoring, IV fluids, blood tests
    ("Malaria", 18000, 4, "Moderate"),            # Antimalarial drugs, blood tests, supportive care
    ("Typhoid", 22000, 7, "Moderate"),            # Antibiotics, Widal test, supportive care
    
    # Respiratory diseases (Winter)
    ("COVID-19", 85000, 10, "Severe"),            # RT-PCR, CT scan, Remdesivir, oxygen support
    ("Pneumonia", 45000, 7, "Severe"),            # Chest X-ray, antibiotics, oxygen, nebulization
    ("Tuberculosis", 35000, 14, "Severe"),        # DOTS treatment, X-ray, sputum tests
    ("Asthma Attack", 12000, 3, "Moderate"),      # Nebulization, steroids, bronchodilators
    
    # Cardiac emergencies (Critical)
    ("Heart Attack", 250000, 12, "Critical"),     # Angiography, stent, ICU, cardiac enzymes
    ("Stroke", 180000, 15, "Critical"),           # CT/MRI brain, thrombolytics, ICU, rehab
    ("Hypertension Crisis", 35000, 5, "Severe"),  # IV antihypertensives, monitoring, tests
    
    # Surgical conditions
    ("Appendicitis", 65000, 5, "Moderate"),       # Appendectomy surgery, anesthesia, recovery
    ("Kidney Stone", 55000, 4, "Moderate"),       # Lithotripsy/PCNL, ultrasound, stent
    ("Fracture", 45000, 7, "Moderate"),           # X-ray, casting/surgery, physiotherapy
    
    # Chronic conditions
    ("Diabetes Complications", 40000, 6, "Moderate"), # Insulin, HbA1c, wound care, monitoring
    ("Liver Disease", 95000, 10, "Severe"),       # LFT, ultrasound, biopsy, medications
    ("Cancer Treatment", 350000, 30, "Critical"), # Chemo cycle, PET scan, tumor markers, support
    
    # GI conditions (Summer)
    ("Gastric Ulcer", 28000, 5, "Moderate"),      # Endoscopy, PPI therapy, H.pylori test
    ("Food Poisoning", 8000, 2, "Mild"),          # IV fluids, antibiotics, stool test
    ("Jaundice", 20000, 7, "Moderate"),           # LFT, hepatitis panel, ultrasound, rest
    
    # Common ailments
    ("Viral Fever", 6000, 3, "Mild"),             # CBC, fever management, rest
]

# =====================================================
# SEASONAL DISEASE PATTERNS (Based on Indian Epidemiology)
# =====================================================
# Real seasonal disease patterns observed in India
SEASONAL_DISEASES = {
    # Monsoon (Jul, Aug, Sep) - Vector-borne and water-borne diseases peak
    'Monsoon': [
        ("Dengue Fever", 0.25),      # Very common - mosquito breeding
        ("Malaria", 0.20),           # Very common - mosquito breeding
        ("Typhoid", 0.15),           # Water contamination
        ("Jaundice", 0.10),          # Hepatitis from contaminated water
        ("Food Poisoning", 0.10),    # Food spoilage in humidity
        ("Viral Fever", 0.10),       # Common infections
        ("Gastric Ulcer", 0.05),     # Stress and irregular eating
        ("Fracture", 0.05),          # Slippery roads, accidents
    ],
    # Winter (Dec, Jan, Feb) - Respiratory diseases peak
    'Winter': [
        ("Pneumonia", 0.20),         # Cold weather respiratory infections
        ("Asthma Attack", 0.18),     # Cold air triggers asthma
        ("Viral Fever", 0.15),       # Flu season
        ("Tuberculosis", 0.12),      # TB spreads in cold, enclosed spaces
        ("Heart Attack", 0.10),      # Cold stress on cardiovascular system
        ("Hypertension Crisis", 0.08), # Blood pressure issues in cold
        ("COVID-19", 0.10),          # Respiratory virus spreads
        ("Stroke", 0.07),            # Cold-related vascular stress
    ],
    # Summer (May, Jun) - Heat-related illnesses
    'Summer': [
        ("Food Poisoning", 0.20),    # Food spoils quickly in heat
        ("Gastric Ulcer", 0.15),     # Dehydration, acidity
        ("Kidney Stone", 0.15),      # Dehydration causes stone formation
        ("Viral Fever", 0.12),       # Summer viruses
        ("Liver Disease", 0.10),     # Heat stress on liver
        ("Diabetes Complications", 0.10), # Heat affects blood sugar
        ("Hypertension Crisis", 0.10), # Heat stress
        ("Fracture", 0.08),          # Outdoor activities increase
    ],
    # Spring (Mar, Apr) - Allergies and transitional diseases
    'Spring': [
        ("Viral Fever", 0.20),       # Seasonal transition viruses
        ("Asthma Attack", 0.18),     # Pollen allergies trigger asthma
        ("Typhoid", 0.12),           # Water issues before monsoon
        ("Gastric Ulcer", 0.10),     # Dietary changes
        ("Food Poisoning", 0.10),    # Temperature fluctuations
        ("Diabetes Complications", 0.10), # Lifestyle changes
        ("Appendicitis", 0.10),      # General surgical
        ("Fracture", 0.10),          # Outdoor activities
    ],
    # Autumn (Oct, Nov) - Post-monsoon diseases
    'Autumn': [
        ("Dengue Fever", 0.18),      # Mosquitoes still active post-monsoon
        ("Malaria", 0.12),           # Tail end of mosquito season
        ("Viral Fever", 0.15),       # Seasonal transition
        ("Typhoid", 0.10),           # Residual water issues
        ("Gastric Ulcer", 0.10),     # Festival season eating
        ("Diabetes Complications", 0.10), # Festival sweets
        ("Heart Attack", 0.10),      # Stress and dietary indulgence
        ("Fracture", 0.08),          # Festival activities
        ("Appendicitis", 0.07),      # General surgical
    ]
}

def get_season_for_month(month):
    """Get season name for a given month (Indian climate)"""
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

def get_disease_for_season(diseases, season):
    """Select a disease based on seasonal probability distribution"""
    seasonal_probs = SEASONAL_DISEASES.get(season, [])
    
    # Build weighted list based on probabilities
    disease_pool = []
    for disease_name, probability in seasonal_probs:
        # Find the disease in our diseases list
        disease = next((d for d in diseases if d['name'] == disease_name), None)
        if disease:
            # Add multiple copies based on probability (scaled to 100)
            copies = int(probability * 100)
            disease_pool.extend([disease] * copies)
    
    # If no seasonal diseases found, return random disease
    if not disease_pool:
        return random.choice(diseases)
    
    return random.choice(disease_pool)

# Doctor Specializations
SPECIALIZATIONS = [
    "General Medicine", "Cardiology", "Neurology", "Orthopedics", "Pediatrics",
    "Gynecology", "Dermatology", "Ophthalmology", "ENT", "Psychiatry",
    "Oncology", "Nephrology", "Gastroenterology", "Pulmonology", "Endocrinology"
]

# Doctor Qualifications
QUALIFICATIONS = [
    "MBBS", "MBBS, MD", "MBBS, MS", "MBBS, MD, DM", "MBBS, MS, MCh",
    "MBBS, DNB", "MBBS, MD, DNB", "MBBS, FRCS"
]

# =====================================================
# DEPARTMENTS / WARDS WITH REALISTIC BED CHARGES
# =====================================================
# Bed charges per day in INR (Private hospital rates in India)
# Format: (Ward Name, Type, Bed Charge Per Day, Total Beds)
DEPARTMENTS_DATA = [
    # Critical Care - Most expensive
    ("ICU", "Critical Care", 8500, 10),           # Ventilator, 24/7 monitoring, specialized staff
    ("Cardiac ICU", "Critical Care", 12000, 8),   # CCU with cardiac monitoring, defibrillator
    
    # Surgical Wards
    ("Surgery Ward", "Surgical", 4500, 10),       # Post-op care, pain management
    ("Orthopedic Ward", "Orthopedic", 3500, 15),  # Traction, physiotherapy access
    
    # Specialty Wards
    ("Oncology Ward", "Oncology", 6000, 12),      # Chemo care, isolation if needed
    ("Maternity Ward", "Maternity", 3500, 20),    # Labor room access, nursing care
    ("Pediatric Ward", "Pediatric", 3000, 20),    # Child-friendly, pediatric nursing
    
    # General Wards - Most affordable
    ("General Ward A", "General", 1800, 30),      # Shared ward, basic amenities
    ("General Ward B", "General", 1800, 30),      # Shared ward, basic amenities
    
    # Emergency
    ("Emergency", "Emergency", 3500, 15),         # 24/7 trauma care, quick response
]

# Shifts
SHIFTS = ["Morning", "Evening", "Night"]
SHIFT_TIMINGS = {
    "Morning": ("06:00", "14:00"),
    "Evening": ("14:00", "22:00"),
    "Night": ("22:00", "06:00")
}

# Doctor Duties
DUTIES = ["Patient Rounds", "OPD Consultation", "Surgery", "Emergency Duty", "ICU Monitoring"]

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def random_phone():
    """Generate Indian phone number"""
    return f"+91 {random.randint(70000, 99999)}{random.randint(10000, 99999)}"

def random_email(name):
    """Generate email from name"""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hospital.org"]
    clean_name = name.lower().replace(" ", ".").replace("dr.", "")
    return f"{clean_name}{random.randint(1, 99)}@{random.choice(domains)}"

def random_date(start_year=2023, end_year=2025):
    """Generate random date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

def indian_name(gender=None):
    """Generate Indian full name"""
    if gender is None:
        gender = random.choice(["M", "F"])
    
    if gender == "M":
        first = random.choice(MALE_FIRST_NAMES)
    else:
        first = random.choice(FEMALE_FIRST_NAMES)
    
    last = random.choice(LAST_NAMES)
    return f"{first} {last}", gender

# =====================================================
# DATA GENERATORS
# =====================================================

def generate_departments():
    """Generate departments data"""
    data = []
    for i, (name, dept_type, charge, beds) in enumerate(DEPARTMENTS_DATA, 1):
        data.append({
            'dept_id': i,
            'name': name,
            'type': dept_type,
            'bed_charge_per_day': charge,
            'total_beds': beds
        })
    return data

def generate_diseases():
    """Generate diseases data"""
    data = []
    for i, (name, cost, days, severity) in enumerate(DISEASES_DATA, 1):
        data.append({
            'disease_id': i,
            'name': name,
            'treatment_cost': cost,
            'avg_stay_days': days,
            'severity': severity
        })
    return data

def generate_doctors(count=50):
    """Generate doctors data"""
    data = []
    for i in range(1, count + 1):
        gender = random.choice(["M", "F"])
        name, _ = indian_name(gender)
        
        data.append({
            'doctor_id': i,
            'name': f"Dr. {name}",
            'gender': gender,
            'specialization': random.choice(SPECIALIZATIONS),
            'qualification': random.choice(QUALIFICATIONS),
            'experience_years': random.randint(2, 30),
            'contact': random_phone(),
            'email': random_email(f"dr.{name}"),
            'is_available': random.choice([True, True, True, False])  # 75% available
        })
    return data

def generate_beds(departments):
    """Generate beds data"""
    data = []
    bed_id = 1
    for dept in departments:
        for bed_num in range(1, dept['total_beds'] + 1):
            is_occupied = random.choice([True, False])
            data.append({
                'bed_id': bed_id,
                'dept_id': dept['dept_id'],
                'bed_number': f"{dept['name'][:3].upper()}-{bed_num:03d}",
                'is_occupied': is_occupied,
                'patient_id': None  # Will be updated with admissions
            })
            bed_id += 1
    return data

def generate_patients(count=150):
    """Generate patients data"""
    data = []
    for i in range(1, count + 1):
        name, gender = indian_name()
        age = random.randint(1, 85)
        
        data.append({
            'patient_id': i,
            'name': name,
            'age': age,
            'gender': gender,
            'contact': random_phone(),
            'email': random_email(name),
            'address': f"{random.randint(1, 500)}, {random.choice(['Main Road', 'MG Road', 'Station Road', 'Gandhi Nagar', 'Nehru Street', 'Patel Colony', 'Sharma Nagar'])}",
            'city': random.choice(CITIES),
            'blood_group': random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
            'emergency_contact': random_phone(),
            'registered_date': random_date().strftime('%Y-%m-%d')
        })
    return data

def generate_doctor_assignments(doctors, departments, count=100):
    """Generate doctor ward assignments"""
    data = []
    for i in range(1, count + 1):
        doctor = random.choice(doctors)
        dept = random.choice(departments)
        shift = random.choice(SHIFTS)
        start_time, end_time = SHIFT_TIMINGS[shift]
        
        data.append({
            'assignment_id': i,
            'doctor_id': doctor['doctor_id'],
            'dept_id': dept['dept_id'],
            'shift': shift,
            'duty_start_time': start_time,
            'duty_end_time': end_time,
            'assigned_date': random_date(2024, 2025).strftime('%Y-%m-%d'),
            'duties': random.choice(DUTIES),
            'status': random.choice(['Active', 'Active', 'Active', 'On Leave'])
        })
    return data

def generate_admissions(patients, doctors, beds, diseases, count=200):
    """Generate admissions data with realistic seasonal disease patterns"""
    data = []
    available_beds = [b for b in beds if not b['is_occupied']]
    
    for i in range(1, min(count + 1, len(patients))):
        patient = patients[i - 1]
        doctor = random.choice(doctors)
        
        # Random admission date
        admit_date = random_date(2024, 2025)
        
        # Get season for this admission date and select disease accordingly
        season = get_season_for_month(admit_date.month)
        disease = get_disease_for_season(diseases, season)
        
        # Some patients discharged, some still admitted
        if random.random() > 0.3:  # 70% discharged
            stay_days = random.randint(disease['avg_stay_days'] - 2, disease['avg_stay_days'] + 5)
            stay_days = max(1, stay_days)
            discharge_date = admit_date + timedelta(days=stay_days)
            status = "Discharged"
        else:
            discharge_date = None
            status = "Admitted"
        
        # Assign a bed if available
        if available_beds:
            bed = available_beds.pop(0)
            bed_id = bed['bed_id']
        else:
            bed_id = random.randint(1, len(beds))
        
        data.append({
            'admission_id': i,
            'patient_id': patient['patient_id'],
            'doctor_id': doctor['doctor_id'],
            'disease_id': disease['disease_id'],
            'bed_id': bed_id,
            'admit_date': admit_date.strftime('%Y-%m-%d'),
            'discharge_date': discharge_date.strftime('%Y-%m-%d') if discharge_date else None,
            'status': status,
            'notes': f"Patient admitted for {disease['name']} treatment"
        })
    return data

def generate_bills(admissions, diseases, departments, beds):
    """Generate bills for discharged patients"""
    data = []
    bill_id = 1
    
    for admission in admissions:
        if admission['status'] == 'Discharged':
            # Get disease info
            disease = next((d for d in diseases if d['disease_id'] == admission['disease_id']), None)
            
            # Get bed and department info
            bed = next((b for b in beds if b['bed_id'] == admission['bed_id']), None)
            if bed:
                dept = next((d for d in departments if d['dept_id'] == bed['dept_id']), None)
            else:
                dept = random.choice(departments)
            
            # Calculate stay days
            admit = datetime.strptime(admission['admit_date'], '%Y-%m-%d')
            discharge = datetime.strptime(admission['discharge_date'], '%Y-%m-%d')
            stay_days = max(1, (discharge - admit).days)
            
            # Calculate charges
            bed_charges = stay_days * dept['bed_charge_per_day']
            treatment_cost = disease['treatment_cost'] if disease else 10000
            doctor_fees = random.randint(1000, 5000)
            other_charges = random.randint(500, 3000)
            
            total = bed_charges + treatment_cost + doctor_fees + other_charges
            
            data.append({
                'bill_id': bill_id,
                'admission_id': admission['admission_id'],
                'patient_id': admission['patient_id'],
                'stay_days': stay_days,
                'bed_charges': bed_charges,
                'treatment_cost': treatment_cost,
                'doctor_fees': doctor_fees,
                'other_charges': other_charges,
                'total_amount': total,
                'status': random.choice(['Paid', 'Paid', 'Paid', 'Pending']),
                'bill_date': admission['discharge_date']
            })
            bill_id += 1
    
    return data

def generate_users():
    """Generate default users"""
    return [
        {
            'user_id': 1,
            'username': 'admin',
            'email': 'admin@hospital.com',
            'password': 'admin123',  # Will be hashed in app
            'role': 'admin',
            'full_name': 'Hospital Admin'
        },
        {
            'user_id': 2,
            'username': 'staff',
            'email': 'staff@hospital.com',
            'password': 'staff123',  # Will be hashed in app
            'role': 'staff',
            'full_name': 'Hospital Staff'
        }
    ]

# =====================================================
# SAVE TO CSV
# =====================================================

def save_to_csv(data, filename, folder='data'):
    """Save data to CSV file"""
    if not data:
        print(f"No data to save for {filename}")
        return
    
    # Create folder if not exists
    os.makedirs(folder, exist_ok=True)
    
    filepath = os.path.join(folder, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✓ Saved {len(data)} records to {filepath}")

# =====================================================
# MAIN - RUN GENERATOR
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("HOSPITAL DATA GENERATOR - INDIAN NAMES")
    print("=" * 50)
    print()
    
    # Generate all data
    print("Generating departments...")
    departments = generate_departments()
    
    print("Generating diseases...")
    diseases = generate_diseases()
    
    print("Generating doctors (50)...")
    doctors = generate_doctors(50)
    
    print("Generating beds...")
    beds = generate_beds(departments)
    
    print("Generating patients (150)...")
    patients = generate_patients(150)
    
    print("Generating doctor assignments (100)...")
    assignments = generate_doctor_assignments(doctors, departments, 100)
    
    print("Generating admissions (200)...")
    admissions = generate_admissions(patients, doctors, beds, diseases, 200)
    
    print("Generating bills...")
    bills = generate_bills(admissions, diseases, departments, beds)
    
    print("Generating users...")
    users = generate_users()
    
    print()
    print("Saving to CSV files...")
    print("-" * 30)
    
    # Save all to CSV
    save_to_csv(departments, 'departments.csv')
    save_to_csv(diseases, 'diseases.csv')
    save_to_csv(doctors, 'doctors.csv')
    save_to_csv(beds, 'beds.csv')
    save_to_csv(patients, 'patients.csv')
    save_to_csv(assignments, 'doctor_assignments.csv')
    save_to_csv(admissions, 'admissions.csv')
    save_to_csv(bills, 'bills.csv')
    save_to_csv(users, 'users.csv')
    
    print()
    print("=" * 50)
    print("DATA GENERATION COMPLETE!")
    print("=" * 50)
