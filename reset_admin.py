#!/usr/bin/env python3
"""
Reset admin user password to admin123
Run this if you can't login with admin/admin123
"""

import sqlite3
from datetime import datetime
import os

# Probeer bcrypt te importeren
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    import hashlib

DB_FILE = "proinvestix_ultimate.db"

def reset_admin():
    """Reset admin password to admin123"""
    
    if not os.path.exists(DB_FILE):
        print(f"Database {DB_FILE} niet gevonden!")
        print("Start eerst de app met: streamlit run app.py")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Maak nieuwe password hash
    if BCRYPT_AVAILABLE:
        admin_hash = bcrypt.hashpw(
            "admin123".encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        print("Using bcrypt for password hash")
    else:
        admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
        print("Using sha256 for password hash (bcrypt not available)")
    
    # Check of admin bestaat
    cursor.execute("SELECT * FROM user_registry WHERE username = 'admin'")
    if cursor.fetchone():
        # Update bestaande admin
        cursor.execute(
            "UPDATE user_registry SET password_hash = ? WHERE username = 'admin'",
            (admin_hash,)
        )
        print("Admin password gereset naar: admin123")
    else:
        # Maak nieuwe admin
        cursor.execute(
            "INSERT INTO user_registry VALUES (?, ?, ?, ?, ?, ?, ?)", 
            ("admin", admin_hash, "SuperAdmin", "admin@proinvestix.ma", 
             1, datetime.now().isoformat(), None)
        )
        print("Admin gebruiker aangemaakt met password: admin123")
    
    conn.commit()
    conn.close()
    
    print("")
    print("Je kunt nu inloggen met:")
    print("  Username: admin")
    print("  Password: admin123")

if __name__ == "__main__":
    reset_admin()
