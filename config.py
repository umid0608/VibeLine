import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TOKEN = str(os.getenv('TOKEN'))
BUGS_GROUP_ID = str(os.getenv('BUGS_GROUP_ID'))
IDEAS_GROUP_ID = str(os.getenv('IDEAS_GROUP_ID'))
RETURN_URL = str(os.getenv('RETURN_URL'))

# Postgres
POSTGRES_USER = str(os.getenv('POSTGRES_USER'))
POSTGRES_PASSWORD = str(os.getenv('POSTGRES_PASSWORD'))
POSTGRES_DB = str(os.getenv('POSTGRES_DB'))
POSTGRES_HOST = str(os.getenv('POSTGRES_HOST'))
POSTGRES_PORT = str(os.getenv('POSTGRES_PORT'))

# Redis
REDIS_HOST = str(os.getenv('REDIS_HOST'))
REDIS_PORT = str(os.getenv('REDIS_PORT'))
# REDIS_DB = str(os.getenv('REDIS_DB'))
REDIS_USER = str(os.getenv('REDIS_USER'))
REDIS_PASSWORD = str(os.getenv('REDIS_PASSWORD'))

