from app import app, db, User

with app.app_context():
    print("--- User Debug Info ---")
    u = User.query.filter_by(username='admin').first()
    if u:
        print(f"User: {u.username}")
        print(f"Role: {u.role}")
        print(f"Password Check (Admin@123): {u.check_password('Admin@123')}")
    else:
        print("User 'admin' not found!")

    # Check other users
    print("\n--- All Users ---")
    users = User.query.all()
    for user in users:
        print(f"ID: {user.user_id}, Username: {user.username}, Role: {user.role}")
