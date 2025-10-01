#!/usr/bin/env python3
"""
Database management utility for MongoDB operations
"""

import os
import sys
import argparse
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import connect_to_mongodb, Service, User, Provider, Booking, Payment, disconnect_from_mongodb


def clear_database():
    """Clear all data from the database"""
    print("⚠️  Clearing all data from the database...")
    confirm = input("Are you sure? This will delete ALL data (yes/no): ")
    if confirm.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    try:
        Service.objects.delete()
        User.objects.delete()
        Provider.objects.delete()
        Booking.objects.delete()
        Payment.objects.delete()
        print("✓ Database cleared successfully!")
    except Exception as e:
        print(f"❌ Error clearing database: {e}")


def show_stats():
    """Show database statistics"""
    try:
        user_count = User.objects.count()
        provider_count = Provider.objects.count()
        service_count = Service.objects.count()
        booking_count = Booking.objects.count()
        payment_count = Payment.objects.count()
        
        print("\n📊 Database Statistics:")
        print(f"Users: {user_count}")
        print(f"Providers: {provider_count}")
        print(f"Services: {service_count}")
        print(f"Bookings: {booking_count}")
        print(f"Payments: {payment_count}")
        
        # Show users by role
        if user_count > 0:
            print("\n👥 Users by Role:")
            for role in ['admin', 'user', 'provider']:
                count = User.objects(role=role).count()
                print(f"  {role.title()}: {count}")
        
        # Show services by category
        if service_count > 0:
            print("\n🔧 Services by Category:")
            pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            categories = Service.objects.aggregate(pipeline)
            for cat in categories:
                print(f"  {cat['_id']}: {cat['count']}")
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")


def list_users():
    """List all users"""
    try:
        users = User.objects()
        if not users:
            print("No users found.")
            return
        
        print("\n👥 Users:")
        print("-" * 80)
        for user in users:
            provider_info = ""
            if user.provider_profile:
                skills = ", ".join(user.provider_profile.skills) if user.provider_profile.skills else "None"
                provider_info = f" | Skills: {skills}"
            
            location_info = ""
            if user.latitude and user.longitude:
                location_info = f" | Location: {user.latitude:.4f}, {user.longitude:.4f}"
            
            print(f"ID: {user.id} | {user.name} ({user.email}) | Role: {user.role}{provider_info}{location_info}")
    
    except Exception as e:
        print(f"❌ Error listing users: {e}")


def list_services():
    """List all services"""
    try:
        services = Service.objects()
        if not services:
            print("No services found.")
            return
        
        print("\n🔧 Services:")
        print("-" * 80)
        for service in services:
            location_info = ""
            if service.location_lat and service.location_lon:
                location_info = f" | Location: {service.location_lat:.4f}, {service.location_lon:.4f}"
            
            print(f"ID: {service.id} | {service.name} | Category: {service.category} | Price: ${service.base_price}{location_info}")
    
    except Exception as e:
        print(f"❌ Error listing services: {e}")


def backup_data():
    """Create a backup of current data"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{timestamp}.json"
        
        print(f"Creating backup: {backup_file}")
        
        # This is a simple backup - in production, use mongodump
        import json
        
        backup_data = {
            'timestamp': timestamp,
            'services': [service.to_json() for service in Service.objects()],
            'users': [user.to_json() for user in User.objects()],
            'providers': [provider.to_json() for provider in Provider.objects()],
            'bookings': [booking.to_json() for booking in Booking.objects()],
            'payments': [payment.to_json() for payment in Payment.objects()]
        }
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"✓ Backup created: {backup_file}")
    
    except Exception as e:
        print(f"❌ Error creating backup: {e}")


def main():
    parser = argparse.ArgumentParser(description='MongoDB Database Manager')
    parser.add_argument('command', choices=['stats', 'clear', 'users', 'services', 'backup'], 
                       help='Command to execute')
    
    args = parser.parse_args()
    
    try:
        # Connect to MongoDB
        connect_to_mongodb()
        print("✓ Connected to MongoDB")
        
        if args.command == 'stats':
            show_stats()
        elif args.command == 'clear':
            clear_database()
        elif args.command == 'users':
            list_users()
        elif args.command == 'services':
            list_services()
        elif args.command == 'backup':
            backup_data()
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        # Disconnect from MongoDB
        disconnect_from_mongodb()


if __name__ == '__main__':
    main()










