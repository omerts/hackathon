import os
import logging
from logging.handlers import RotatingFileHandler

log_file_path = '/var/log/nakaiathon'
log_level = 'INFO'

os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(level=getattr(logging, log_level), format="%(asctime)s [%(levelname)s] %(message)s", handlers=[
  RotatingFileHandler(log_file_path, 
                              mode='a',
                              maxBytes=26*1024*1024, 
                              backupCount=2, 
                              encoding=None, 
                              delay=0),
  logging.StreamHandler()
])

logger = logging