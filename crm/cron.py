"""
Cron jobs for the CRM application
"""

import os
import sys
from datetime import datetime
import requests

def log_crm_heartbeat():
    """
    Log a heartbeat message every 5 minutes to confirm CRM application health
    """
    try:
        # Get current timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        
        # Log heartbeat message
        log_message = f"{timestamp} CRM is alive\n"
        
        with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
            f.write(log_message)
        
        # Optionally query the GraphQL hello field to verify endpoint is responsive
        try:
            response = requests.post(
                'http://localhost:8000/graphql/',
                json={'query': '{ hello }'},
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('hello'):
                    # Log successful GraphQL query
                    graphql_log = f"{timestamp} GraphQL endpoint is responsive\n"
                    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                        f.write(graphql_log)
                else:
                    # Log GraphQL response issue
                    graphql_log = f"{timestamp} GraphQL endpoint responded but with unexpected data\n"
                    with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                        f.write(graphql_log)
            else:
                # Log GraphQL error
                graphql_log = f"{timestamp} GraphQL endpoint returned status {response.status_code}\n"
                with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                    f.write(graphql_log)
                    
        except requests.exceptions.RequestException as e:
            # Log GraphQL connection error
            graphql_log = f"{timestamp} GraphQL endpoint connection error: {str(e)}\n"
            with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                f.write(graphql_log)
        
        return True
        
    except Exception as e:
        # Log any other errors
        try:
            timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
            error_log = f"{timestamp} CRM heartbeat error: {str(e)}\n"
            with open('/tmp/crm_heartbeat_log.txt', 'a') as f:
                f.write(error_log)
        except:
            pass
        return False


def update_low_stock():
    """
    Execute the UpdateLowStockProducts mutation via the GraphQL endpoint
    and log updated product names and new stock levels
    """
    try:
        # GraphQL mutation to update low stock products
        mutation = """
        mutation UpdateLowStockProducts {
            updateLowStockProducts {
                updatedProducts {
                    id
                    name
                    stock
                    price
                }
                successMessage
                errors
            }
        }
        """
        
        # Make GraphQL request
        response = requests.post(
            'http://localhost:8000/graphql/',
            json={'query': mutation},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get('data', {}).get('updateLowStockProducts', {})
            
            if result.get('errors'):
                # Log errors
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                error_log = f"{timestamp} - Low stock update errors: {result['errors']}\n"
                with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                    f.write(error_log)
                return False
            
            # Log successful updates
            updated_products = result.get('updatedProducts', [])
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if updated_products:
                log_message = f"{timestamp} - Low stock update successful\n"
                for product in updated_products:
                    product_log = f"{timestamp} - Product: {product['name']}, New Stock: {product['stock']}\n"
                    log_message += product_log
            else:
                log_message = f"{timestamp} - No low stock products found to update\n"
            
            # Write to log file
            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                f.write(log_message)
            
            return True
            
        else:
            # Log GraphQL error
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_log = f"{timestamp} - GraphQL request failed with status {response.status_code}\n"
            with open('/tmp/low_stock_updates_log.txt', 'a') as f:
                f.write(error_log)
            return False
            
    except requests.exceptions.RequestException as e:
        # Log connection error
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_log = f"{timestamp} - Connection error: {str(e)}\n"
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(error_log)
        return False
        
    except Exception as e:
        # Log any other errors
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_log = f"{timestamp} - Unexpected error: {str(e)}\n"
        with open('/tmp/low_stock_updates_log.txt', 'a') as f:
            f.write(error_log)
        return False
