bind = "127.0.0.1:5001"
backlog = 2048

workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

max_requests = 1000
max_requests_jitter = 50

limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Security settings
forwarded_allow_ips = "127.0.0.1"
secure_scheme_headers = {"X-FORWARDED-PROTO": "https"}

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "pathfinder_pro"
preload_app = True

# Performance
enable_stdio_inheritance = True 