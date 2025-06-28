#!/usr/bin/env python3
"""
Simple test script to verify the web interface is working
"""
import requests
import time

def test_web_interface():
    """Test the web interface endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing Airplanes Live API web interface...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint working")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Health endpoint error: {e}")
    
    # Test main page
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✓ Main page working")
        else:
            print(f"✗ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Main page error: {e}")
    
    # Test API endpoint
    try:
        response = requests.get(f"{base_url}/api/airplanes", timeout=10)
        if response.status_code == 200:
            print("✓ API endpoint working")
            data = response.json()
            if 'ac' in data:
                print(f"  Found {len(data['ac'])} aircraft")
            else:
                print("  No aircraft data in response")
        else:
            print(f"✗ API endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ API endpoint error: {e}")

if __name__ == "__main__":
    test_web_interface() 