#!/usr/bin/env python
"""
Simple test script for the GraphQL CRM system.
"""

import requests
import json

GRAPHQL_URL = "http://localhost:8000/graphql"

def test_query(query):
    """Test a GraphQL query"""
    payload = {"query": query}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    print("🚀 Testing GraphQL CRM System")
    print("=" * 40)
    
    # Test 1: Basic hello query
    print("\n1. Testing hello query...")
    result = test_query("{ hello }")
    if "data" in result and result["data"]["hello"] == "Hello, GraphQL!":
        print("✅ Hello query successful")
    else:
        print("❌ Hello query failed:", result)
    
    # Test 2: Query all customers
    print("\n2. Testing customer query...")
    result = test_query("{ allCustomers { name email } }")
    if "data" in result and "allCustomers" in result["data"]:
        print(f"✅ Found {len(result['data']['allCustomers'])} customers")
    else:
        print("❌ Customer query failed:", result)
    
    # Test 3: Query all products
    print("\n3. Testing product query...")
    result = test_query("{ allProducts { name price stock } }")
    if "data" in result and "allProducts" in result["data"]:
        print(f"✅ Found {len(result['data']['allProducts'])} products")
    else:
        print("❌ Product query failed:", result)
    
    # Test 4: Query all orders
    print("\n4. Testing order query...")
    result = test_query("{ allOrders { id customer { name } totalAmount } }")
    if "data" in result and "allOrders" in result["data"]:
        print(f"✅ Found {len(result['data']['allOrders'])} orders")
    else:
        print("❌ Order query failed:", result)
    
    print("\n🎉 Basic tests completed!")
    print("Visit http://localhost:8000/graphql for the GraphQL playground")

if __name__ == "__main__":
    main()
