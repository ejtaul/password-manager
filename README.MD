# 🔐 Secure Password Manager

A command-line password manager built with Python that securely stores and manages your passwords using industry-standard encryption.

## ✨ Features

- **🔒 Military-Grade Encryption**: Uses Fernet (AES-128) symmetric encryption to protect your passwords
- **🔑 Master Password Protection**: Single master password to access all stored credentials
- **🎲 Strong Password Generator**: Create cryptographically secure random passwords
- **📊 SQLite Database**: Lightweight local storage with no internet dependency
- **🛡️ Secure Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000 iterations
- **👁️ Password Retrieval**: Safely view and copy stored passwords
- **🗑️ Easy Management**: Add, view, retrieve, and delete password entries

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/password-manager.git
cd password-manager
```

2. **Create virtual environment**
```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python password_manager.py
```

## 📖 Usage

### First-Time Setup
When you run the application for the first time, you'll be prompted to create a master password:

```
=== First Time Setup ===
Create a strong master password. This will encrypt all your passwords.
Enter master password: ********
Confirm master password: ********
✓ Master password created successfully!
```

**⚠️ IMPORTANT**: Your master password cannot be recovered if lost. Store it safely!

### Main Menu Options

```
1. Add new password       - Store a new password entry
2. View all passwords     - List all stored services
3. Retrieve password      - Decrypt and view a specific password
4. Delete password        - Remove a password entry
5. Generate random password - Create a strong password
6. Exit                   - Close the application
```

### Adding a Password

```
=== Add New Password ===
Service name (e.g., Gmail, GitHub): GitHub
Username/Email: user@example.com

1. Generate strong password
2. Enter your own password
Choice (1/2): 1

Password length (default 16): 20
Include symbols? (y/n, default y): y

✓ Generated password: xK9@mP2#vL8$nQ4&wR7!
✓ Password for GitHub saved successfully!
```

### Retrieving a Password

```
Enter service name: GitHub

=== Passwords for 'GitHub' ===

Username: user@example.com
Password: xK9@mP2#vL8$nQ4&wR7!
```

## 🏗️ Project Structure

```
password-manager/
│
├── password_manager.py    # Main application code
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
├── password_vault.db     # SQLite database (created on first run)
└── master.key           # Encryption key (created on first run)
```

## 🔒 Security Features

### Encryption
- **Algorithm**: Fernet (symmetric encryption using AES-128 in CBC mode)
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000 iterations
- **Salt**: Unique 32-byte random salt per master password

### Password Generation
- Uses Python's `secrets` module for cryptographically strong randomness
- Customizable length and character sets
- Default 16-character passwords with uppercase, lowercase, digits, and symbols

### Best Practices Implemented
- Master password never stored in plaintext
- Passwords encrypted before database storage
- Secure password input using `getpass` (hidden input)
- Rate limiting on master password attempts (3 attempts)

## 🛠️ Technical Details

### Dependencies
- **cryptography**: Provides Fernet encryption
- **sqlite3**: Built-in Python database
- **hashlib**: Built-in cryptographic hashing
- **secrets**: Built-in cryptographically secure random generation

### Database Schema

**master table**
```sql
id             INTEGER PRIMARY KEY
password_hash  TEXT NOT NULL
salt           TEXT NOT NULL
```

**passwords table**
```sql
id          INTEGER PRIMARY KEY AUTOINCREMENT
service     TEXT NOT NULL
username    TEXT NOT NULL
password    TEXT NOT NULL (encrypted)
created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

## ⚠️ Security Considerations

### Do's ✅
- Use a strong, unique master password (12+ characters)
- Back up `password_vault.db` and `master.key` together
- Store backups in encrypted locations only
- Keep the application and dependencies updated

### Don'ts ❌
- Never share your master password
- Don't commit `master.key` or `password_vault.db` to version control
- Don't use the same master password elsewhere
- Don't store the master password in plain text anywhere

### Limitations
- **Local storage only**: Not cloud-synced across devices
- **Single user**: No multi-user support
- **CLI-based**: No graphical user interface
- **No password recovery**: Lost master password means lost access

## 🚀 Future Enhancements

Potential features for future versions:
- [ ] GUI interface using Tkinter
- [ ] Password strength analyzer
- [ ] Breach detection integration
- [ ] Cloud sync capability
- [ ] Two-factor authentication
- [ ] Password history tracking
- [ ] Auto-fill browser extension
- [ ] Mobile app version




## 🙏 Acknowledgments

- Built with Python's `cryptography` library
- Inspired by modern password manager architecture
- Follows OWASP password storage guidelines



---

**⚠️ Disclaimer**: This is an educational project. While it implements strong security practices, it has not undergone professional security auditing. For critical password storage, consider established solutions like Bitwarden, 1Password, or KeePass.