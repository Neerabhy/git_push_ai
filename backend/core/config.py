import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# 1. Force Python to find and load the .env file immediately
load_dotenv()

# 2. Quick debug print to prove whether Python sees it or not
# (This will print in your terminal when you run Uvicorn)
print("=== DEBUG INFO ===")
print("Did Python find GROQ_API_KEY?:", "GROQ_API_KEY" in os.environ)
print("==================")

class Settings(BaseSettings):
    GROQ_API_KEY: str
    APP_NAME: str = "CrewAI Travel Planner API"
    DEBUG_MODE: bool = True

settings = Settings()