from app import app, db, Bill

with app.app_context():
    print("--- Revenue Debug Info ---")
    try:
        revenue = db.session.query(db.func.sum(Bill.total_amount)).filter(Bill.status == 'Paid').scalar()
        print(f"Total Revenue: {revenue}")
    except Exception as e:
        print(f"Error calculating revenue: {e}")
        import traceback
        traceback.print_exc()
