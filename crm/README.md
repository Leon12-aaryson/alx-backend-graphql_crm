# CRM Application Setup Guide

This guide provides step-by-step instructions for setting up and running the CRM application with all its scheduled tasks and background workers.

## Prerequisites

- Python 3.8+
- Django 5.2.5+
- Redis server
- Virtual environment (recommended)

## Installation

1. **Clone the repository and navigate to the project directory:**
   ```bash
   cd alx-backend-graphql_crm
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Django migrations:**
   ```bash
   python manage.py migrate
   ```

## Redis Setup

1. **Install Redis:**
   - **macOS:** `brew install redis`
   - **Ubuntu/Debian:** `sudo apt-get install redis-server`
   - **Windows:** Download from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)

2. **Start Redis server:**
   ```bash
   redis-server
   ```

3. **Verify Redis is running:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

## Running the Application

### 1. Start Django Development Server
```bash
python manage.py runserver
```
The GraphQL endpoint will be available at: http://localhost:8000/graphql/

### 2. Start Celery Worker
In a new terminal:
```bash
celery -A crm worker -l info
```

### 3. Start Celery Beat (Scheduler)
In another new terminal:
```bash
celery -A crm beat -l info
```

## Scheduled Tasks

### Django-Crontab Jobs
The following cron jobs are configured to run automatically:

1. **CRM Heartbeat** - Every 5 minutes
   - Logs: `/tmp/crm_heartbeat_log.txt`
   - Function: `crm.cron.log_crm_heartbeat`

2. **Low Stock Updates** - Every 12 hours (at 00:00 and 12:00)
   - Logs: `/tmp/low_stock_updates_log.txt`
   - Function: `crm.cron.update_low_stock`

### Celery Beat Tasks
The following tasks are scheduled with Celery Beat:

1. **Weekly CRM Report** - Every Monday at 6:00 AM
   - Logs: `/tmp/crm_report_log.txt`
   - Task: `crm.tasks.generate_crm_report`

### Manual Scripts
The following scripts can be run manually or added to system crontab:

1. **Customer Cleanup** - `crm/cron_jobs/clean_inactive_customers.sh`
   - Removes customers with no orders in the last year
   - Logs: `/tmp/customer_cleanup_log.txt`
   - Crontab: `0 2 * * 0` (Every Sunday at 2:00 AM)

2. **Order Reminders** - `crm/cron_jobs/send_order_reminders.py`
   - Processes orders from the last 7 days
   - Logs: `/tmp/order_reminders_log.txt`
   - Crontab: `0 8 * * *` (Daily at 8:00 AM)

## Adding Scripts to System Crontab

To add the manual scripts to your system crontab:

1. **View current crontab:**
   ```bash
   crontab -l
   ```

2. **Edit crontab:**
   ```bash
   crontab -e
   ```

3. **Add the following lines:**
   ```bash
   # Customer cleanup - Every Sunday at 2:00 AM
   0 2 * * 0 /path/to/alx-backend-graphql_crm/crm/cron_jobs/clean_inactive_customers.sh
   
   # Order reminders - Daily at 8:00 AM
   0 8 * * * /path/to/alx-backend-graphql_crm/crm/cron_jobs/send_order_reminders.py
   ```

4. **Save and exit** (the editor will depend on your system)

## Managing Django-Crontab Jobs

### Add/Remove Cron Jobs
```bash
# Add cron jobs to system crontab
python manage.py crontab add

# Remove cron jobs from system crontab
python manage.py crontab remove

# Show current cron jobs
python manage.py crontab show
```

## Monitoring and Logs

All scheduled tasks and scripts log their activities to files in `/tmp/`:

- `/tmp/crm_heartbeat_log.txt` - CRM heartbeat logs
- `/tmp/low_stock_updates_log.txt` - Low stock update logs
- `/tmp/crm_report_log.txt` - Weekly CRM report logs
- `/tmp/customer_cleanup_log.txt` - Customer cleanup logs
- `/tmp/order_reminders_log.txt` - Order reminder logs

## Troubleshooting

### Common Issues

1. **Redis Connection Error:**
   - Ensure Redis server is running: `redis-server`
   - Check Redis connection: `redis-cli ping`

2. **Celery Worker Not Starting:**
   - Verify Django settings are correct
   - Check that Redis is accessible
   - Ensure all dependencies are installed

3. **Cron Jobs Not Running:**
   - Check system crontab: `crontab -l`
   - Verify script permissions: `chmod +x script.sh`
   - Check log files for errors

4. **GraphQL Endpoint Unavailable:**
   - Ensure Django server is running
   - Check for any Django errors in the console

### Debug Mode

For debugging, you can run tasks manually:

```bash
# Test Celery task
python manage.py shell
>>> from crm.tasks import generate_crm_report
>>> generate_crm_report.delay()

# Test cron functions
python manage.py shell
>>> from crm.cron import log_crm_heartbeat
>>> log_crm_heartbeat()
```

## Production Considerations

- Use a production-ready Redis server
- Configure proper logging instead of `/tmp/` files
- Set up monitoring for Celery workers
- Use environment variables for sensitive configuration
- Consider using Supervisor or systemd for process management

## Support

For issues or questions, check the log files first, then review the Django and Celery documentation.
