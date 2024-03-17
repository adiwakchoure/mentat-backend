import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import marvin

marvin.settings.openai.api_key = os.getenv("OPENAI_API_KEY")

from brave import Brave

braveSync = Brave(api_key=os.getenv("BRAVE_API_KEY"))

from tavily import TavilyClient

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Try to get DATABASE_URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not set in environment variables.")
