bind = "127.0.0.1:8005"
workers = 2

accesslog = "-" 
errorlog = "-" 
worker_class = "sync"
timeout = 30
loglevel = "info"
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' %(D)s"


