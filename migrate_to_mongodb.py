#!/usr/bin/env python3
"""
Data migration script to seed MongoDB with initial services
Run this script to initialize your MongoDB database with sample data
"""

import os
import sys
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import connect_to_mongodb, Service, User, Provider


def seed_services():
    """Seed the database with initial services"""
    print("Seeding services...")
    
    # Check if services already exist
    if Service.objects.count() > 0:
        print("Services already exist, skipping seeding...")
        return
    
    services = [
        {
            'name': 'Electrician',
            'category': 'Electrical',
            'base_price': 20.0,
            'description': 'Professional electrical services for home and office'
        },
        {
            'name': 'Plumber',
            'category': 'Plumbing',
            'base_price': 18.0,
            'description': 'Complete plumbing solutions and repairs'
        },
        {
            'name': 'Carpenter',
            'category': 'Woodwork',
            'base_price': 22.0,
            'description': 'Custom woodwork and furniture repair'
        },
        {
            'name': 'Cleaner',
            'category': 'Cleaning',
            'base_price': 15.0,
            'description': 'Professional cleaning services'
        },
        {
            'name': 'Painter',
            'category': 'Painting',
            'base_price': 16.0,
            'description': 'Interior and exterior painting services'
        },
        {
            'name': 'Gardener',
            'category': 'Landscaping',
            'base_price': 14.0,
            'description': 'Garden maintenance and landscaping'
        },
        {
            'name': 'Locksmith',
            'category': 'Security',
            'base_price': 25.0,
            'description': 'Lock installation and repair services'
        },
        {
            'name': 'HVAC Technician',
            'category': 'Heating & Cooling',
            'base_price': 30.0,
            'description': 'Heating, ventilation, and air conditioning services'
        }
    ]
    
    for service_data in services:
        service = Service(
            name=service_data['name'],
            category=service_data['category'],
            base_price=service_data['base_price']
        )
        service.save()
        print(f"✓ Created service: {service_data['name']}")
    
    print(f"Successfully seeded {len(services)} services!")


def seed_sample_users():
    """Create sample users for testing"""
    print("\nSeeding sample users...")
    
    # Check if users already exist
    if User.objects.count() > 0:
        print("Users already exist, skipping seeding...")
        return
    
    sample_users = [
        {
            'name': 'Admin User',
            'email': 'admin@hofix.com',
            'password': 'admin123',
            'role': 'admin',
            'phone': '+1-555-0001'
        },
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'user123',
            'role': 'user',
            'phone': '+1-555-0002'
        },
        {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'password': 'provider123',
            'role': 'provider',
            'phone': '+1-555-0003',
            'skills': ['Electrician', 'Plumber'],
            'location': {'lat': 40.7128, 'lon': -74.0060}
        },
        {
            'name': 'Mike Johnson',
            'email': 'mike@example.com',
            'password': 'provider123',
            'role': 'provider',
            'phone': '+1-555-0004',
            'skills': ['Carpenter', 'Painter'],
            'location': {'lat': 40.7589, 'lon': -73.9851}
        }
    ]
    
    from extensions import bcrypt
    
    for user_data in sample_users:
        # Hash the password
        password_hash = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        
        user = User(
            name=user_data['name'],
            email=user_data['email'],
            password_hash=password_hash,
            role=user_data['role'],
            phone=user_data['phone'],
            rating=5.0
        )
        
        # Add location if provided
        if 'location' in user_data:
            user.latitude = user_data['location']['lat']
            user.longitude = user_data['location']['lon']
        
        user.save()
        
        # Create provider profile if role is provider
        if user_data['role'] == 'provider':
            provider = Provider(
                user=user,
                skills=user_data.get('skills', []),
                availability=True
            )
            provider.save()
            user.provider_profile = provider
            user.save()
            print(f"✓ Created provider: {user_data['name']}")
        else:
            print(f"✓ Created user: {user_data['name']}")
    
    print(f"Successfully seeded {len(sample_users)} users!")


def main():
    """Main migration function"""
    print("🚀 Starting MongoDB migration...")
    
    try:
        # Initialize MongoDB connection
        connect_to_mongodb()
        print("✓ Connected to MongoDB")
        
        # Seed services
        seed_services()
        
        # Seed sample users
        seed_sample_users()
        
        print("\n🎉 Migration completed successfully!")
        print("\nSample login credentials:")
        print("Admin: admin@hofix.com / admin123")
        print("User: john@example.com / user123")
        print("Provider: jane@example.com / provider123")
        print("Provider: mike@example.com / provider123")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()










