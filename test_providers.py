#!/usr/bin/env python3
"""
Simple test script to verify provider functionality
"""
import requests
import json

def test_providers():
    base_url = "http://localhost:5000"
    
    print("Testing provider endpoints...")
    
    # Test 1: Create test providers
    print("\n1. Creating test providers...")
    try:
        response = requests.post(f"{base_url}/debug/create-test-providers")
        if response.status_code == 200:
            print("✅ Test providers created successfully")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to create test providers: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating test providers: {e}")
    
    # Test 2: Get debug provider info
    print("\n2. Getting provider debug info...")
    try:
        response = requests.get(f"{base_url}/debug/providers")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data.get('total_providers', 0)} providers")
            for provider in data.get('providers', []):
                print(f"  - {provider.get('user_name', 'Unknown')} (Skills: {provider.get('skills', [])})")
        else:
            print(f"❌ Failed to get provider info: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting provider info: {e}")
    
    # Test 3: Get nearby providers
    print("\n3. Getting nearby providers...")
    try:
        response = requests.get(f"{base_url}/providers/nearby?lat=28.6139&lon=77.2090")
        if response.status_code == 200:
            providers = response.json()
            print(f"✅ Found {len(providers)} nearby providers")
            for provider in providers:
                print(f"  - {provider.get('name', 'Unknown')} ({provider.get('distance_km', 0)} km away)")
        else:
            print(f"❌ Failed to get nearby providers: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting nearby providers: {e}")
    
    # Test 4: Get nearby providers with service filter
    print("\n4. Getting nearby electricians...")
    try:
        response = requests.get(f"{base_url}/providers/nearby?lat=28.6139&lon=77.2090&service_type=electrician")
        if response.status_code == 200:
            providers = response.json()
            print(f"✅ Found {len(providers)} electricians nearby")
            for provider in providers:
                print(f"  - {provider.get('name', 'Unknown')} (Skills: {provider.get('skills', [])})")
        else:
            print(f"❌ Failed to get electricians: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting electricians: {e}")

if __name__ == "__main__":
    test_providers()

