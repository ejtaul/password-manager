"""
Secure Password Manager
A CLI-based password manager with encryption
Author: Your Name
"""

import sqlite3
import hashlib
import secrets
import string
from cryptography.fernet import Fernet
from getpass import getpass
import os
import base64

class PasswordManager:
    def __init__(self):
        self.db_name = "password_vault.db"
        self.key_file = "master.key"
        self.cipher = None
        self.setup_database()
    
    def setup_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Table for master password hash
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master (
                id INTEGER PRIMARY KEY,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        ''')
        
        # Table for stored passwords
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def derive_key(self, master_password, salt):
        """Derive encryption key from master password"""
        kdf = hashlib.pbkdf2_hmac('sha256', master_password.encode(), salt, 100000)
        return base64.urlsafe_b64encode(kdf[:32])
    
    def setup_master_password(self):
        """First-time setup for master password"""
        print("\n=== First Time Setup ===")
        print("Create a strong master password. This will encrypt all your passwords.")
        
        while True:
            master = getpass("Enter master password: ")
            confirm = getpass("Confirm master password: ")
            
            if master == confirm and len(master) >= 8:
                # Generate salt and hash
                salt = secrets.token_bytes(32)
                password_hash = hashlib.sha256(master.encode() + salt).hexdigest()
                
                # Store master password hash
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO master (password_hash, salt) VALUES (?, ?)",
                             (password_hash, salt.hex()))
                conn.commit()
                conn.close()
                
                # Generate and store encryption key
                key = self.derive_key(master, salt)
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                
                self.cipher = Fernet(key)
                print("\n✓ Master password created successfully!")
                return True
            elif len(master) < 8:
                print("❌ Password must be at least 8 characters long.\n")
            else:
                print("❌ Passwords don't match. Try again.\n")
    
    def verify_master_password(self):
        """Verify the master password"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash, salt FROM master WHERE id=1")
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return self.setup_master_password()
        
        stored_hash, salt_hex = result
        salt = bytes.fromhex(salt_hex)
        
        attempts = 3
        while attempts > 0:
            master = getpass("\nEnter master password: ")
            password_hash = hashlib.sha256(master.encode() + salt).hexdigest()
            
            if password_hash == stored_hash:
                key = self.derive_key(master, salt)
                self.cipher = Fernet(key)
                print("✓ Access granted!")
                return True
            else:
                attempts -= 1
                if attempts > 0:
                    print(f"❌ Incorrect password. {attempts} attempts remaining.")
                else:
                    print("❌ Too many failed attempts. Exiting.")
                    return False
        
        return False
    
    def generate_password(self, length=16, use_symbols=True):
        """Generate a strong random password"""
        characters = string.ascii_letters + string.digits
        if use_symbols:
            characters += string.punctuation
        
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password
    
    def add_password(self):
        """Add a new password entry"""
        print("\n=== Add New Password ===")
        service = input("Service name (e.g., Gmail, GitHub): ").strip()
        username = input("Username/Email: ").strip()
        
        choice = input("\n1. Generate strong password\n2. Enter your own password\nChoice (1/2): ").strip()
        
        if choice == '1':
            length = input("Password length (default 16): ").strip()
            length = int(length) if length.isdigit() else 16
            use_symbols = input("Include symbols? (y/n, default y): ").strip().lower() != 'n'
            password = self.generate_password(length, use_symbols)
            print(f"\n✓ Generated password: {password}")
        else:
            password = getpass("Enter password: ")
        
        # Encrypt and store
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
                     (service, username, encrypted_password))
        conn.commit()
        conn.close()
        
        print(f"\n✓ Password for {service} saved successfully!")
    
    def view_passwords(self):
        """View all stored passwords"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT id, service, username, created_at FROM passwords ORDER BY service")
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print("\n📭 No passwords stored yet.")
            return
        
        print("\n=== Stored Passwords ===")
        for row in results:
            print(f"\n[{row[0]}] {row[1]}")
            print(f"    Username: {row[2]}")
            print(f"    Created: {row[3]}")
    
    def retrieve_password(self):
        """Retrieve and decrypt a specific password"""
        service = input("\nEnter service name: ").strip()
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM passwords WHERE service LIKE ?", 
                     (f"%{service}%",))
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            print(f"\n❌ No password found for '{service}'")
            return
        
        print(f"\n=== Passwords for '{service}' ===")
        for username, encrypted_password in results:
            decrypted_password = self.cipher.decrypt(encrypted_password.encode()).decode()
            print(f"\nUsername: {username}")
            print(f"Password: {decrypted_password}")
    
    def delete_password(self):
        """Delete a password entry"""
        self.view_passwords()
        
        try:
            pwd_id = int(input("\nEnter password ID to delete: ").strip())
            confirm = input(f"Are you sure you want to delete entry {pwd_id}? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM passwords WHERE id=?", (pwd_id,))
                conn.commit()
                conn.close()
                print("\n✓ Password deleted successfully!")
            else:
                print("\n✗ Deletion cancelled.")
        except ValueError:
            print("\n❌ Invalid ID.")
    
    def run(self):
        """Main application loop"""
        print("=" * 50)
        print("🔐  SECURE PASSWORD MANAGER")
        print("=" * 50)
        
        if not self.verify_master_password():
            return
        
        while True:
            print("\n" + "=" * 50)
            print("1. Add new password")
            print("2. View all passwords")
            print("3. Retrieve password")
            print("4. Delete password")
            print("5. Generate random password")
            print("6. Exit")
            print("=" * 50)
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                self.add_password()
            elif choice == '2':
                self.view_passwords()
            elif choice == '3':
                self.retrieve_password()
            elif choice == '4':
                self.delete_password()
            elif choice == '5':
                length = input("Password length (default 16): ").strip()
                length = int(length) if length.isdigit() else 16
                use_symbols = input("Include symbols? (y/n, default y): ").strip().lower() != 'n'
                pwd = self.generate_password(length, use_symbols)
                print(f"\n✓ Generated password: {pwd}")
            elif choice == '6':
                print("\n👋 Goodbye! Your passwords are secure.")
                break
            else:
                print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    manager = PasswordManager()
    manager.run()