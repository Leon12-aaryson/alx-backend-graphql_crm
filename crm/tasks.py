"""
Celery tasks for the CRM application
"""

import os
import sys
from datetime import datetime
import requests
from celery import shared_task

# Add the project directory to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()

from django.db.models import Sum, Count
from crm.models import Customer, Order


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report summarizing total orders, customers, and revenue
    """
    try:
        # GraphQL query to fetch CRM statistics
        query = """
        query GetCRMStats {
            allCustomers {
                id
            }
            allOrders {
                id
                totalAmount
            }
        }
        """
        
        # Make GraphQL request
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': query},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            customers_data = data.get('data', {}).get('allCustomers', [])
            orders_data = data.get('data', {}).get('allOrders', [])
            
            # Calculate statistics
            total_customers = len(customers_data)
            total_orders = len(orders_data)
            total_revenue = sum(float(order['totalAmount']) for order in orders_data)
            
            # Format timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Create report message
            report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue\n"
            
            # Log the report
            with open('/tmp/crm_report_log.txt', 'a') as f:
                f.write(report_message)
            
            print(f"CRM report generated successfully: {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue")
            return True
            
        else:
            # Log GraphQL error
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_log = f"{timestamp} - GraphQL request failed with status {response.status_code}\n"
            with open('/tmp/crm_report_log.txt', 'a') as f:
                f.write(error_log)
            return False
            
    except requests.exceptions.RequestException as e:
        # Log connection error
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_log = f"{timestamp} - Connection error: {str(e)}\n"
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(error_log)
        return False
        
    except Exception as e:
        # Log any other errors
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_log = f"{timestamp} - Unexpected error: {str(e)}\n"
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(error_log)
        return False


@shared_task
def generate_crm_report_django_orm():
    """
    Alternative implementation using Django ORM directly (fallback method)
    """
    try:
        # Use Django ORM to get statistics
        total_customers = Customer.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Format timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create report message
        report_message = f"{timestamp} - Report (Django ORM): {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue\n"
        
        # Log the report
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(report_message)
        
        print(f"CRM report generated successfully (Django ORM): {total_customers} customers, {total_orders} orders, ${total_revenue:.2f} revenue")
        return True
        
    except Exception as e:
        # Log any errors
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_log = f"{timestamp} - Django ORM error: {str(e)}\n"
        with open('/tmp/crm_report_log.txt', 'a') as f:
            f.write(error_log)
        return False
