"""
Script to create an admin user for SEFCNet
==========================================
Run this script to quickly create an admin user
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from auth.database import init_db, get_db
from auth.security import get_password_hash, Role, Permission
from auth.auth_service import AuthService, UserCreate


async def create_admin_user(email: str, password: str):
    """Create an admin user"""
    # Initialize database
    await init_db()
    
    # Check if user already exists
    db = await get_db()
    existing = await db.get_user_by_email(email)
    if existing:
        print(f"❌ User with email {email} already exists!")
        return False
    
    # Create admin user
    try:
        user_data = UserCreate(
            email=email,
            password=password,
            roles=[Role.ADMIN],
            permissions=[Permission.ADMIN, Permission.MANAGE, Permission.WRITE, Permission.READ]
        )
        
        user = await AuthService.register_user(user_data)
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {user.email}")
        print(f"   ID: {user.id}")
        print(f"   Roles: {[r.value for r in user.roles]}")
        print(f"   Permissions: {[p.value for p in user.permissions]}")
        return True
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create an admin user for SEFCNet")
    parser.add_argument("--email", default="admin@sefcnet.com", help="Admin email")
    parser.add_argument("--password", default="admin123", help="Admin password")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()
        if not email or not password:
            print("❌ Email and password are required!")
            sys.exit(1)
    else:
        email = args.email
        password = args.password
        print(f"Creating admin user with:")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print(f"\n⚠️  For production, use --interactive and set a strong password!")
    
    success = asyncio.run(create_admin_user(email, password))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

