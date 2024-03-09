import os
import logging
from logging.handlers import RotatingFileHandler

current_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(current_directory, 'log')

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