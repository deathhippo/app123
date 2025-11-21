from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

# Initialize the Database Manager
db = SQLAlchemy()

# Initialize the Cache Manager (This makes it run faster)
# It stores data in RAM (memory) for 60 seconds so it doesn't read the disk constantly.
cache = Cache(config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 60})