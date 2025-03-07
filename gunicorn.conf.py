# Number of worker processes
workers = 4

# Number of threads per worker
threads = 2

# Bind to a specific address and port
bind = "0.0.0.0:8000"

# Timeout for worker processes (in seconds)
timeout = 120

# Logging configuration
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stdout
loglevel = "info"

# Application module
wsgi_app = "core.wsgi:application"

# Maximum number of requests a worker will process before restarting
max_requests = 1000

# Maximum number of requests a worker will process before gracefully restarting
max_requests_jitter = 50

# Preload the application before forking worker processes
preload_app = True

# Set environment variables
raw_env = [
    "DJANGO_SETTINGS_MODULE=core.settings",
    "DEBUG=False",
]