#!/usr/bin/env python
"""
Test script for the GraphQL CRM system.
This script tests all the major functionality including queries, mutations, and error handling.
"""

import requests
import json
import time

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

def make_request(query, operation_name=None, variables=None):
    """Make a GraphQL request"""
    payload = {
        "query": query
    }
    if operation_name:
        payload["operationName"] = operation_name
    if variables:
        payload["variables"] = variables
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def test_basic_query():
    """Test the basic hello query"""
    print("🔍 Testing basic hello query...")
    query = "{ hello }"
    result = make_request(query)
    
    if "data" in result and result["data"]["hello"] == "Hello, GraphQL!":
        print("✅ Basic query successful")
        return True
    else:
        print("❌ Basic query failed:", result)
        return False

def test_customer_queries():
    """Test customer-related queries"""
    print("\n🔍 Testing customer queries...")
    
    # Test all customers
    query = "{ allCustomers { id name email phone createdAt } }"
    result = make_request(query)
    
    if "data" in result and "allCustomers" in result["data"]:
        customers = result["data"]["allCustomers"]
        print(f"✅ Found {len(customers)} customers")
        
        # Test individual customer query
        if customers:
            customer_id = customers[0]["id"]
            query = f'{{ customer(id: "{customer_id}") {{ name email }} }}'
            result = make_request(query)
            
            if "data" in result and result["data"]["customer"]:
                print("✅ Individual customer query successful")
                return True
            else:
                print("❌ Individual customer query failed:", result)
                return False
    else:
        print("❌ All customers query failed:", result)
        return False

def test_product_queries():
    """Test product-related queries"""
    print("\n🔍 Testing product queries...")
    
    # Test all products
    query = "{ allProducts { id name price stock createdAt } }"
    result = make_request(query)
    
    if "data" in result and "allProducts" in result["data"]:
        products = result["data"]["allProducts"]
        print(f"✅ Found {len(products)} products")
        
        # Test individual product query
        if products:
            product_id = products[0]["id"]
            query = f'{{ product(id: "{product_id}") {{ name price stock }} }}'
            result = make_request(query)
            
            if "data" in result and result["data"]["product"]:
                print("✅ Individual product query successful")
                return True
            else:
                print("❌ Individual product query failed:", result)
                return False
    else:
        print("❌ All products query failed:", result)
        return False

def test_order_queries():
    """Test order-related queries"""
    print("\n🔍 Testing order queries...")
    
    # Test all orders
    query = "{ allOrders { id customer { name email } totalAmount orderDate } }"
    result = make_request(query)
    
    if "data" in result and "allOrders" in result["data"]:
        orders = result["data"]["allOrders"]
        print(f"✅ Found {len(orders)} orders")
        
        # Test individual order query
        if orders:
            order_id = orders[0]["id"]
            query = f'{{ order(id: "{order_id}") {{ customer {{ name }} totalAmount }} }}'
            result = make_request(query)
            
            if "data" in result and result["data"]["order"]:
                print("✅ Individual order query successful")
                return True
            else:
                print("❌ Individual order query failed:", result)
                return False
    else:
        print("❌ All orders query failed:", result)
        return False

def test_customer_mutations():
    """Test customer mutations"""
    print("\n🔍 Testing customer mutations...")
    
    # Test creating a customer
    mutation = """
    mutation {
        createCustomer(input: {
            name: "Test Customer",
            email: "testcustomer@example.com",
            phone: "555-123-4567"
        }) {
            customer {
                id
                name
                email
                phone
            }
            message
            errors
        }
    }
    """
    
    result = make_request(mutation)
    
    if "data" in result and result["data"]["createCustomer"]["customer"]:
        print("✅ Create customer successful")
        
        # Test bulk create customers
        bulk_mutation = """
        mutation {
            bulkCreateCustomers(input: [
                { name: "Bulk Customer 1", email: "bulk1@example.com" },
                { name: "Bulk Customer 2", email: "bulk2@example.com", phone: "555-111-2222" }
            ]) {
                customers {
                    id
                    name
                    email
                }
                errors
            }
        }
        """
        
        result = make_request(bulk_mutation)
        
        if "data" in result and result["data"]["bulkCreateCustomers"]["customers"]:
            print("✅ Bulk create customers successful")
            return True
        else:
            print("❌ Bulk create customers failed:", result)
            return False
    else:
        print("❌ Create customer failed:", result)
        return False

def test_product_mutations():
    """Test product mutations"""
    print("\n🔍 Testing product mutations...")
    
    # Test creating a product
    mutation = """
    mutation {
        createProduct(input: {
            name: "Test Product",
            price: 29.99,
            stock: 100
        }) {
            product {
                id
                name
                price
                stock
            }
            errors
        }
    }
    """
    
    result = make_request(mutation)
    
    if "data" in result and result["data"]["createProduct"]["product"]:
        print("✅ Create product successful")
        return True
    else:
        print("❌ Create product failed:", result)
        return False

def test_order_mutations():
    """Test order mutations"""
    print("\n🔍 Testing order mutations...")
    
    # Test creating an order
    mutation = """
    mutation {
        createOrder(input: {
            customerId: "1",
            productIds: ["1", "3"]
        }) {
            order {
                id
                customer {
                    name
                }
                totalAmount
                orderDate
            }
            errors
        }
    }
    """
    
    result = make_request(mutation)
    
    if "data" in result and result["data"]["createOrder"]["order"]:
        print("✅ Create order successful")
        return True
    else:
        print("❌ Create order failed:", result)
        return False

def test_error_handling():
    """Test error handling"""
    print("\n🔍 Testing error handling...")
    
    # Test duplicate email
    mutation = """
    mutation {
        createCustomer(input: {
            name: "Duplicate Email",
            email: "alice@example.com",
            phone: "555-123-4567"
        }) {
            customer {
                id
                name
                email
            }
            message
            errors
        }
    }
    """
    
    result = make_request(mutation)
    
    if "data" in result and result["data"]["createCustomer"]["errors"]:
        print("✅ Duplicate email error handling successful")
        
        # Test invalid phone format
        mutation = """
        mutation {
            createCustomer(input: {
                name: "Invalid Phone",
                email: "invalidphone@example.com",
                phone: "invalid-phone"
            }) {
                customer {
                    id
                    name
                    email
                }
                message
                errors
            }
        }
        """
        
        result = make_request(mutation)
        
        if "data" in result and result["data"]["createCustomer"]["errors"]:
            print("✅ Invalid phone format error handling successful")
            return True
        else:
            print("❌ Invalid phone format error handling failed:", result)
            return False
    else:
        print("❌ Duplicate email error handling failed:", result)
        return False

def main():
    """Run all tests"""
    print("🚀 Starting GraphQL CRM System Tests")
    print("=" * 50)
    
    tests = [
        test_basic_query,
        test_customer_queries,
        test_product_queries,
        test_order_queries,
        test_customer_mutations,
        test_product_mutations,
        test_order_mutations,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The GraphQL CRM system is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    print("\n🌐 You can now use the GraphQL playground at: http://localhost:8000/graphql")

if __name__ == "__main__":
    main()
