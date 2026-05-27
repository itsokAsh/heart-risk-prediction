"""Debug script to check authentication status."""
from sqlalchemy import create_engine, text
from app.auth import hash_password, verify_password

engine = create_engine("postgresql://heartguard:heartguard@postgres:5432/heartguard")
with engine.connect() as conn:
    result = conn.execute(text("SELECT email, hashed_password FROM users WHERE email = 'ashcr2004@gmail.com'"))
    row = result.fetchone()
    if row:
        email, hashed = row
        print(f"User found: {email}")
        print(f"Hash: {hashed[:60]}...")
        print(f"Hash type: {type(hashed)}")
        
        # Test a new hash to confirm pwdlib works
        test_hash = hash_password("testpass")
        print(f"\nNew test hash: {test_hash[:60]}...")
        print(f"Verify test hash: {verify_password('testpass', test_hash)}")
        
        # Check if the stored hash format is valid
        print(f"\nStored hash starts with: {hashed[:10]}")
    else:
        print("User NOT found in database!")
