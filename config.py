import os
from dotenv import load_dotenv
import pathlib


env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
class Config:
    GROQ_TOKEN = os.getenv("GROQ_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME")
    DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
    CARS_DB_PATH = os.path.join(os.path.dirname(__file__), "data/cars.json")
    DEBUG = True
if not Config.GROQ_TOKEN or not Config.MODEL_NAME:
    raise ValueError("GROQ_TOKEN or MODEL_NAME not set in environment")
