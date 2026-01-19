from app import app, db, Patient, Admission, Bed, Doctor, Bill, Alert, Department
from app import check_and_create_alerts

with app.app_context():
    print("--- Dashboard Debug ---")
    try:
        print("1. Counting Patients...")
        c1 = Patient.query.count()
        print(f"Patients: {c1}")
        
        print("2. Counting Admitted...")
        c2 = Admission.query.filter_by(status='Admitted').count()
        print(f"Admitted: {c2}")
        
        print("3. Checking Beds...")
        c3 = Bed.query.filter_by(is_occupied=False).count()
        print(f"Free Beds: {c3}")
        
        print("4. Checking Doctors...")
        c4 = Doctor.query.filter_by(is_available=True).count()
        print(f"Doctors: {c4}")
        
        print("5. Checking Pending Bills...")
        c5 = Bill.query.filter_by(status='Pending').count()
        print(f"Pending Bills: {c5}")
        
        print("6. Recent Admissions...")
        adm = Admission.query.order_by(Admission.admit_date.desc()).limit(5).all()
        print(f"Recent: {len(adm)}")
        
        print("7. Alerts...")
        alerts = Alert.query.filter_by(is_read=False).order_by(Alert.created_at.desc()).limit(5).all()
        print(f"Alerts: {len(alerts)}")

        print("8. Check and Create Alerts function...")
        check_and_create_alerts()
        print("Alerts check done.")
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
