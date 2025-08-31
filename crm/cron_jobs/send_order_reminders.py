#!/usr/bin/env python3
"""
Order Reminder Script
Queries GraphQL endpoint for orders within the last 7 days and logs reminders
"""

import os
import sys
from datetime import datetime, timedelta
import requests
import json

# Add the project directory to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.utils import timezone
from crm.models import Order

def send_order_reminders():
    """Query orders from the last 7 days and log reminders"""
    
    # Calculate date 7 days ago
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    # GraphQL query to get orders from the last 7 days
    query = """
    query GetRecentOrders($since: DateTime!) {
        allOrders {
            id
            orderDate
            totalAmount
            customer {
                id
                name
                email
            }
        }
    }
    """
    
    # Variables for the GraphQL query
    variables = {
        "since": seven_days_ago.isoformat()
    }
    
    try:
        # Make GraphQL request
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={
                'query': query,
                'variables': variables
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('data', {}).get('allOrders', [])
            
            # Filter orders from the last 7 days (in case GraphQL filtering doesn't work)
            recent_orders = []
            for order in orders:
                order_date = datetime.fromisoformat(order['orderDate'].replace('Z', '+00:00'))
                if order_date >= seven_days_ago:
                    recent_orders.append(order)
            
            # Log the reminders
            timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"{timestamp} - Processing {len(recent_orders)} recent orders\n"
            
            for order in recent_orders:
                customer_email = order['customer']['email']
                order_id = order['id']
                total_amount = order['totalAmount']
                
                reminder_line = f"{timestamp} - Order {order_id}: Customer {customer_email}, Amount: ${total_amount}\n"
                log_message += reminder_line
            
            # Write to log file
            with open('/tmp/order_reminders_log.txt', 'a') as f:
                f.write(log_message)
            
            print(f"Order reminders processed! Found {len(recent_orders)} recent orders.")
            return len(recent_orders)
            
        else:
            print(f"GraphQL request failed with status code: {response.status_code}")
            return 0
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to GraphQL endpoint. Make sure the server is running on localhost:8000")
        return 0
    except Exception as e:
        print(f"Error processing order reminders: {str(e)}")
        return 0

if __name__ == "__main__":
    send_order_reminders()
