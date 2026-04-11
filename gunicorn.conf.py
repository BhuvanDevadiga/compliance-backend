import multiprocessing
import os

workers = 4
worker_class = "uvicorn.workers.UvicornWorker"

bind = "0.0.0.0:8000"
backlog = 2048

timeout = 30
graceful_timeout = 30
keepalive = 5

max_requests = 10000
max_requests_jitter = 1000

accesslog = "-"
errorlog = "-"
loglevel = "info"

preload_app = True
worker_tmp_dir = "/dev/shm"
