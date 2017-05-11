import os
from app import app as application
print('loading')
print(os.environ.get('DATABASE_URL'))