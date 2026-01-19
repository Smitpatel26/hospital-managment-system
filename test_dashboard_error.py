from app import app, db, User
from flask import url_for
from flask_login import login_user

with app.app_context():
    with app.test_request_context():
        print("=" * 60)
        print("TESTING DASHBOARD ROUTE")
        print("=" * 60)
        
        # Step 1: Get admin user
        print("\n1. Getting admin user...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("❌ Admin user not found!")
            exit(1)
        print(f"✅ Found: {admin.username} (role: {admin.role})")
        
        # Step 2: Simulate login
        print("\n2. Simulating login...")
        login_user(admin)
        print(f"✅ User logged in")
        
        # Step 3: Try to call dashboard function
        print("\n3. Calling dashboard() function...")
        try:
            from app import dashboard
            result = dashboard()
            print(f"✅ Dashboard returned successfully")
            print(f"   Response type: {type(result)}")
        except Exception as e:
            print(f"❌ DASHBOARD ERROR: {e}")
            print("\nFull traceback:")
            import traceback
            traceback.print_exc()
            
            # Write to file for inspection
            with open("dashboard_error.log", "w") as f:
                f.write(f"Error: {e}\n\n")
                traceback.print_exc(file=f)
            print("\n✅ Error details written to dashboard_error.log")
