from crewai import Agent
from config import Config
from schemas.schemas import BookingToolCall

receptionist = Agent(
    role="Receptionist",
    goal="Handle customer booking of test drives",
    backstory="You are an AI receptionist for a car dealership.",
    llm={
        "model": Config.LLM_MODEL,
        "temperature": 0,
        "response_format": BookingToolCall,  
    },
    verbose=True
)
