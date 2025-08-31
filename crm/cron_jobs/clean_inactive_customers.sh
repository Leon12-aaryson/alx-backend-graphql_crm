#!/bin/bash

# Customer Cleanup Script
# Deletes customers with no orders since a year ago

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to the project directory
cd "$PROJECT_DIR"

# Execute Django command to clean up inactive customers
python manage.py shell << EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

# Calculate date 1 year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since a year ago
customers_to_delete = []
for customer in Customer.objects.all():
    # Check if customer has any orders in the last year
    recent_orders = Order.objects.filter(
        customer=customer,
        order_date__gte=one_year_ago
    )
    if not recent_orders.exists():
        customers_to_delete.append(customer)

# Delete the customers
deleted_count = len(customers_to_delete)
for customer in customers_to_delete:
    customer.delete()

# Log the results
timestamp = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
log_message = f"{timestamp} - Deleted {deleted_count} inactive customers\n"

with open('/tmp/customer_cleanup_log.txt', 'a') as f:
    f.write(log_message)

print(f"Deleted {deleted_count} inactive customers")
EOF
