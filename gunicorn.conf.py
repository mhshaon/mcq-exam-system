# Gunicorn configuration for MCQ Exam System

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/gunicorn/mcq-exam-access.log"
errorlog = "/var/log/gunicorn/mcq-exam-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "mcq-exam"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/mcq-exam.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (uncomment when SSL is configured)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Preload app for better performance
preload_app = True

# Environment variables
raw_env = [
    'DJANGO_SETTINGS_MODULE=config.settings_production',
]
