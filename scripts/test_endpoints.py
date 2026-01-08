import requests
import time
import sys
from threading import Thread
import subprocess

def test():
    # Give server time to start
    time.sleep(5)
    
    try:
        # Test Index
        r_index = requests.get('http://127.0.0.1:8001/')
        print(f"Index Status: {r_index.status_code}")
        
        # Test API
        r_api = requests.get('http://127.0.0.1:8001/api/properties/')
        print(f"API Properties Status: {r_api.status_code}")
        print(f"API Properties Data: {r_api.json()}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
