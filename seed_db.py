#!/usr/bin/env python
"""
Database seeding script for the GraphQL CRM system.
Run this script to populate the database with sample data.
"""

import os
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order, OrderItem


def seed_customers():
    """Seed sample customers"""
    customers_data = [
        {
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'phone': '+1234567890'
        },
        {
            'name': 'Bob Smith',
            'email': 'bob@example.com',
            'phone': '123-456-7890'
        },
        {
            'name': 'Carol Davis',
            'email': 'carol@example.com',
            'phone': '+1-555-123-4567'
        },
        {
            'name': 'David Wilson',
            'email': 'david@example.com',
            'phone': '555.123.4567'
        }
    ]
    
    created_customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
        if created:
            created_customers.append(customer)
            print(f"Created customer: {customer.name}")
        else:
            print(f"Customer already exists: {customer.name}")
    
    return created_customers


def seed_products():
    """Seed sample products"""
    products_data = [
        {
            'name': 'Laptop',
            'price': Decimal('999.99'),
            'stock': 10
        },
        {
            'name': 'Smartphone',
            'price': Decimal('599.99'),
            'stock': 25
        },
        {
            'name': 'Headphones',
            'price': Decimal('99.99'),
            'stock': 50
        },
        {
            'name': 'Tablet',
            'price': Decimal('399.99'),
            'stock': 15
        },
        {
            'name': 'Wireless Mouse',
            'price': Decimal('29.99'),
            'stock': 100
        }
    ]
    
    created_products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            created_products.append(product)
            print(f"Created product: {product.name} - ${product.price}")
        else:
            print(f"Product already exists: {product.name}")
    
    return created_products


def seed_orders(customers, products):
    """Seed sample orders"""
    orders_data = [
        {
            'customer': customers[0],  # Alice
            'products': [products[0], products[2]],  # Laptop + Headphones
        },
        {
            'customer': customers[1],  # Bob
            'products': [products[1], products[3]],  # Smartphone + Tablet
        },
        {
            'customer': customers[2],  # Carol
            'products': [products[4]],  # Wireless Mouse
        },
        {
            'customer': customers[3],  # David
            'products': [products[0], products[1], products[2]],  # Laptop + Smartphone + Headphones
        }
    ]
    
    created_orders = []
    for data in orders_data:
        # Calculate total amount
        total_amount = sum(product.price for product in data['products'])
        
        # Create order
        order = Order.objects.create(
            customer=data['customer'],
            total_amount=total_amount
        )
        
        # Create order items
        for product in data['products']:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )
        
        created_orders.append(order)
        print(f"Created order: {order} - Total: ${order.total_amount}")
    
    return created_orders


def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    # Seed customers
    print("\n--- Seeding Customers ---")
    customers = seed_customers()
    
    # Seed products
    print("\n--- Seeding Products ---")
    products = seed_products()
    
    # Seed orders
    print("\n--- Seeding Orders ---")
    orders = seed_orders(customers, products)
    
    print(f"\nSeeding completed!")
    print(f"Created {len(customers)} customers")
    print(f"Created {len(products)} products")
    print(f"Created {len(orders)} orders")
    
    print("\nYou can now test the GraphQL API at http://localhost:8000/graphql")


if __name__ == '__main__':
    main()
