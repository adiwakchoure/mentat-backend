# fastapi_neon/settings.py

from starlette.config import Config

from starlette.datastructures import Secret


try:

    config = Config(".env")

except FileNotFoundError:

    config = Config()


# DATABASE_URL = config("DATABASE_URL", cast=Secret)
DATABASE_URL = "postgresql://neondb_owner:HKk1JzmsA5cP@ep-purple-thunder-a5aqu41b.us-east-2.aws.neon.tech/neondb?sslmode=require"
