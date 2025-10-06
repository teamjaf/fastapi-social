# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:9090"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "fast-social-api"

# Server mechanics
daemon = False
pidfile = "/tmp/fast-social-api.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
