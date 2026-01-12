"""
Helper script to generate password hashes for new users.
Run this script to generate a bcrypt hash that you can use in environment variables.

Usage:
    python generate_password_hash.py
"""

import bcrypt

def generate_password_hash():
    """Generate a bcrypt password hash for a new user."""
    print("Password Hash Generator")
    print("=" * 50)
    
    password = input("Enter the password to hash: ")
    
    if not password:
        print("Error: Password cannot be empty!")
        return
    
    # Generate bcrypt hash
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    print("\n" + "=" * 50)
    print("Generated Password Hash:")
    print("=" * 50)
    print(hashed_password)
    print("=" * 50)
    print("\nAdd this to your environment variables:")
    print(f"USER_<USERNAME>_PASSWORD_HASH={hashed_password}")
    print("\nExample for user 'admin':")
    print(f"USER_ADMIN_PASSWORD_HASH={hashed_password}")
    print("\nAlso set:")
    print("USER_ADMIN_NAME=Admin User")
    print("USER_ADMIN_EMAIL=admin@example.com")

if __name__ == "__main__":
    generate_password_hash()
