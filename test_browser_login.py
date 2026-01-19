import requests
import re

# URL of the local server
BASE_URL = 'http://127.0.0.1:5000'

def test_login():
    session = requests.Session()
    
    print(f"1. Accessing Login Page...")
    try:
        r = session.get(f'{BASE_URL}/login')
        print(f"   Status: {r.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running?")
        return

    print(f"2. Attempting Login (admin)...")
    payload = {
        'username': 'admin',
        'password': 'Admin@123'
    }
    r = session.post(f'{BASE_URL}/login', data=payload)
    print(f"   Status: {r.status_code}")
    print(f"   URL after login: {r.url}")
    
    if 'dashboard' in r.url:
        print("✅ Login Redirected to Dashboard!")
        if "Dashboard" in r.text or "Total Patients" in r.text:
            print("✅ Dashboard Content Found!")
        else:
            print("❌ Dashboard Content NOT Found! dumping text...")
            print(r.text[:500])
    else:
        print("❌ Login Failed or did not redirect to dashboard.")
        print(f"   Content dump: {r.text[:500]}")

if __name__ == '__main__':
    test_login()
