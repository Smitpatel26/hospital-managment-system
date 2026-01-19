from app import app, db, User

with app.app_context():
    # Find admin user
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f"Found admin user: {admin.username}")
        print(f"Current role: {admin.role}")
        
        # Reset password to Admin@123
        admin.set_password('Admin@123')
        admin.role = 'admin'  # Ensure role is correct
        db.session.commit()
        
        print("✅ Password reset to: Admin@123")
        print("✅ Role set to: admin")
        
        # Verify
        if admin.check_password('Admin@123'):
            print("✅ Password verification successful!")
        else:
            print("❌ Password verification failed!")
    else:
        print("❌ Admin user not found!")
        print("\nAll users:")
        for u in User.query.all():
            print(f"  - {u.username} ({u.role})")
