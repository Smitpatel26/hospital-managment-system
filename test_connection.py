# Test different passwords
import psycopg2

passwords_to_try = [
    'smit@2609',
    'Smit@2609',
    'SMIT@2609',
    'smit2609',
    'Smit2609',
    'postgres',
    'admin',
    'password',
    '123456',
    '1234',
    'smit',
    'Smit',
]

print("Testing PostgreSQL passwords...")
print("=" * 40)

for pwd in passwords_to_try:
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password=pwd,
            connect_timeout=3
        )
        print(f"✅ SUCCESS! Password is: {pwd}")
        conn.close()
        break
    except Exception as e:
        print(f"❌ Failed: {pwd}")
else:
    print("\n" + "=" * 40)
    print("None of the passwords worked.")
    print("Please open pgAdmin 4 and check/reset your password.")
