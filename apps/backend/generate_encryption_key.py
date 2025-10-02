#!/usr/bin/env python3
"""
Encryption Key Generation Tool
===============================

Generate cryptographically secure keys for API encryption.

Usage:
    python3 generate_encryption_key.py

Output:
    - ENCRYPTION_MASTER_KEY: Master password for key derivation
    - ENCRYPTION_SALT: Unique salt for PBKDF2

Security Note:
    Store these values securely in .env file (NEVER commit to version control)
"""

import os
import base64


def generate_key() -> str:
    """Generate a 32-byte cryptographically secure random key."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')


def main():
    print("=" * 70)
    print("🔐 Encryption Key Generator for mynanobananaapp")
    print("=" * 70)
    print()

    master_key = generate_key()
    salt = generate_key()

    print("Generated secure encryption keys:")
    print()
    print("📋 Add these to your .env file:")
    print("-" * 70)
    print(f"ENCRYPTION_MASTER_KEY={master_key}")
    print(f"ENCRYPTION_SALT={salt}")
    print("-" * 70)
    print()

    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("  1. Store these keys in .env file (located in apps/backend/.env)")
    print("  2. NEVER commit .env file to version control")
    print("  3. Add .env to .gitignore")
    print("  4. Backup these keys securely (loss = data loss)")
    print("  5. Use different keys for development and production")
    print()

    print("✅ Keys generated successfully!")
    print()

    # Offer to write directly to .env file
    response = input("Would you like to write these to apps/backend/.env? (y/n): ").strip().lower()

    if response == 'y':
        env_path = 'apps/backend/.env'

        # Check if .env already exists
        if os.path.exists(env_path):
            print(f"⚠️  {env_path} already exists!")
            overwrite = input("Overwrite existing keys? This will break existing encrypted data! (y/n): ").strip().lower()
            if overwrite != 'y':
                print("Cancelled. Please manually add the keys above to your .env file.")
                return

        # Write to .env file
        with open(env_path, 'a') as f:
            f.write("\n# ========================================\n")
            f.write("# Encryption Keys (Generated: AUTO)\n")
            f.write("# ========================================\n")
            f.write(f"ENCRYPTION_MASTER_KEY={master_key}\n")
            f.write(f"ENCRYPTION_SALT={salt}\n")
            f.write("\n")

        print(f"✅ Keys written to {env_path}")
        print("⚠️  Make sure .env is in .gitignore!")

    else:
        print("Cancelled. Please manually add the keys above to your .env file.")


if __name__ == '__main__':
    main()
