from crewai.tools import tool
import json
import os
from datetime import datetime
from config import Config

@tool("query_knowledge_base")
def query_knowledge_base(query: str) -> str:
    """
    Mandatory tool to check car inventory. Returns available models (SUV, Sedan), 
    variants (Standard, Luxury, Sport), and features. Use this to guide the user.
    """
    try:

        path = Config.CARS_DB_PATH
        if not os.path.exists(path):
            return "Error: Car database file not found."
            
        with open(path, "r") as f:
            data = json.load(f)
        return f"Available Inventory: {json.dumps(data)}"
    except Exception as e:
        return f"Error reading car database: {e}"

# @tool("book_test_drive")
# def book_test_drive(model: str, date: str, time: str) -> str:
#     """
#     Final step tool. Use ONLY when model, date, and time are all provided by the user.
#     Args:
#         model: The validated car model name.
#         date: YYYY-MM-DD.
#         time: HH:MM format.
#     """
#     try:
#         booking_id = datetime.now().strftime("%H%M%S")
#         confirmation = f"Booking confirmed for {model} on {date} at {time}. Ref: BK-{booking_id}."
        
#         os.makedirs("logs", exist_ok=True)
#         with open("logs/bookings.txt", "a") as f:
#             f.write(f"{datetime.now()}: {confirmation}\n")

#         return confirmation
#     except Exception as e:
#         return f"Booking failed: {str(e)}"
    

@tool("book_test_drive")
def book_test_drive(model: str, date: str, time: str) -> str:
    """
    Final step tool. Use ONLY when model, date, and time are all provided by the user.
    Args:
        model: The validated car model name.
        date: YYYY-MM-DD.
        time: HH:MM format.
    """
    # GUARDRAIL: Check if the Agent is trying to use a 'placeholder' or guess
    # You can add more logic here to check against the 'current_date'
    if not model or not date or not time:
        return "ERROR: Missing information. You must ask the user for the specific model, date, and time before calling this tool."

    try:
        # Create a clean booking
        booking_id = datetime.now().strftime("%H%M%S")
        confirmation = f"Booking confirmed for {model} on {date} at {time}. Ref: BK-{booking_id}."
        
        os.makedirs("logs", exist_ok=True)
        with open("logs/bookings.txt", "a") as f:
            f.write(f"{datetime.now()}: {confirmation}\n")

        return confirmation
    except Exception as e:
        return f"Booking failed: {str(e)}"