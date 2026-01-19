# from crewai import Agent
# from config import Config
# from schemas.schemas import BookingToolCall

# receptionist = Agent(
#     role="Receptionist",
#     goal="Handle customer booking of test drives",
#     backstory="You are an AI receptionist for a car dealership.",
#     llm={
#         "model": Config.LLM_MODEL,
#         "temperature": 0,
#         "response_format": BookingToolCall,  
#     },
#     verbose=True
# )



from crewai import Agent
from config import Config

receptionist = Agent(
    role="Sales Assistant",
    goal="Guide users through car inventory and only book test drives when specific details are provided.",
    backstory=(
        "You are a professional car dealership assistant. "
        "Your primary rule: NEVER guess, assume, or hallucinate a date or time. "
        "If the user says 'I want to book', you MUST ask 'Which model, what date, and what time?' "
        "Only call the 'book_test_drive' tool if the user has EXPLICITLY provided: "
        "1. The car model (e.g., SUV or Sedan) "
        "2. A specific date (e.g., tomorrow, next Monday, or Jan 20th) "
        "3. A specific time (e.g., 10:00 AM). "
        "If any of these are missing, stay in conversation mode and ask for them using <speech> tags."
    ),
    llm={
        "model": Config.MODEL_NAME,
        "temperature": 0,  # Keep it at 0 to prevent creative guessing
    },
    verbose=True,
    allow_delegation=False
)