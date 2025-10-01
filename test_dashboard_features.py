#!/usr/bin/env python3
"""
Test script to verify the new dashboard features
"""
import requests
import json
import time

def test_dashboard_features():
    base_url = "http://localhost:5000"
    
    print("Testing Dashboard Features...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connection...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return
    
    # Test 2: Check services endpoint
    print("\n2. Testing services endpoint...")
    try:
        response = requests.get(f"{base_url}/services")
        if response.status_code == 200:
            services = response.json()
            print(f"✅ Services endpoint working - {len(services)} services found")
            if services:
                print(f"   Sample service: {services[0].get('name')} - ₹{services[0].get('base_price')}")
        else:
            print(f"❌ Services endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Services endpoint error: {e}")
    
    # Test 3: Check user dashboard route
    print("\n3. Testing user dashboard route...")
    try:
        response = requests.get(f"{base_url}/dashboard/user")
        if response.status_code == 200:
            print("✅ User dashboard route accessible")
        else:
            print(f"❌ User dashboard route failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User dashboard route error: {e}")
    
    # Test 4: Check provider dashboard route
    print("\n4. Testing provider dashboard route...")
    try:
        response = requests.get(f"{base_url}/dashboard/provider")
        if response.status_code == 200:
            print("✅ Provider dashboard route accessible")
        else:
            print(f"❌ Provider dashboard route failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Provider dashboard route error: {e}")
    
    # Test 5: Check services catalog route
    print("\n5. Testing services catalog route...")
    try:
        response = requests.get(f"{base_url}/services")
        if response.status_code == 200:
            print("✅ Services catalog route accessible")
        else:
            print(f"❌ Services catalog route failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Services catalog route error: {e}")
    
    # Test 6: Check booking map route
    print("\n6. Testing booking map route...")
    try:
        response = requests.get(f"{base_url}/booking-map")
        if response.status_code == 200:
            print("✅ Booking map route accessible")
        else:
            print(f"❌ Booking map route failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Booking map route error: {e}")
    
    print("\n" + "=" * 50)
    print("Dashboard Features Test Complete!")
    print("\nNext Steps:")
    print("1. Login as a user and check the dashboard")
    print("2. Create a booking and verify real-time updates")
    print("3. Login as a provider and check notifications")
    print("4. Test the rating system with completed bookings")
    print("5. Test live provider tracking")

if __name__ == "__main__":
    test_dashboard_features()

