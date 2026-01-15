# from crewai.tools import tool
# import json
# from config import Config

# @tool("query_knowledge_base")
# def query_knowledge_base(query: str):
#     """Searches the car database for models, features, and pricing."""
#     try:
#         with open(Config.CARS_DB_PATH, "r") as f:
#             data = json.load(f)
#         return json.dumps(data)
#     except Exception as e:
#         return f"Error accessing database: {e}"

# @tool("book_test_drive")
# def book_test_drive(model: str, date: str, time: str):
#     """Books a test drive. Requires car model, date, and time."""
#     return f"SUCCESS: Test drive for {model} confirmed on {date} at {time}."


# from crewai.tools import tool
# import json
# from config import Config

# @tool(
#     "query_knowledge_base",
#     description="Given a query, search the car inventory and return models, specs, and features."
# )
# def query_knowledge_base(query: str):
#     try:
#         with open(Config.CARS_DB_PATH, "r") as f:
#             data = json.load(f)
#         return json.dumps(data)
#     except Exception as e:
#         return f"Error reading car database: {e}"

# @tool(
#     "book_test_drive",
#     description="Book a test drive with a model, date, and time string."
# )
# def book_test_drive(model: str, date: str, time: str):
#     return f"SUCCESS: Test drive for {model} confirmed on {date} at {time}."





# from crewai.tools import tool
# import json
# from config import Config

# @tool("query_knowledge_base")
# def query_knowledge_base(query: str) -> str:
#     """
#     Search car inventory and return models, specs, and features.
#     """
#     try:
#         with open(Config.CARS_DB_PATH, "r") as f:
#             data = json.load(f)
#         return json.dumps(data)
#     except Exception as e:
#         return f"Error reading car database: {e}"

# @tool("book_test_drive")
# def book_test_drive(model: str, date: str, time: str) -> str:
#     """
#     Book a test drive for the given model, date, and time.
#     """
#     return f"SUCCESS: Test drive for {model} confirmed on {date} at {time}."



# from crewai.tools import tool
# import json
# import os
# from datetime import datetime
# from config import Config

# @tool("query_knowledge_base")
# def query_knowledge_base(query: str) -> str:
#     """
#     Search car inventory and return models, specs, and features. 
#     Use this when a customer asks about what cars are available or specific details.
#     """
#     try:
#         with open(Config.CARS_DB_PATH, "r") as f:
#             data = json.load(f)
#         return json.dumps(data)
#     except Exception as e:
#         return f"Error reading car database: {e}"

# @tool("book_test_drive")
# def book_test_drive(model: str, date: str, time: str) -> str:
#     """
#     Book a test drive for a specific car model, date, and time.
#     Arguments:
#         model: The name of the car (e.g., 'SUV', 'Nissan X-Trail')
#         date: The date in YYYY-MM-DD format
#         time: The time of the appointment (e.g., '10:00 AM')
#     """
#     try:
#         # Create a confirmation message
#         booking_id = datetime.now().strftime("%H%M%S")
#         confirmation = (
#             f"SUCCESS: Booking confirmed for {model}. "
#             f"Reference ID: BK-{booking_id}. "
#             f"Scheduled for {date} at {time}."
#         )

#         # Ensure a directory for logs exists
#         os.makedirs("logs", exist_ok=True)

#         # Log the booking to a file so you can verify it worked
#         with open("logs/bookings.txt", "a") as f:
#             f.write(f"{datetime.now()}: {confirmation}\n")

#         return confirmation

#     except Exception as e:
#         return f"Error processing booking: {str(e)}"


############################



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
        # Resolve path correctly
        path = Config.CARS_DB_PATH
        if not os.path.exists(path):
            return "Error: Car database file not found."
            
        with open(path, "r") as f:
            data = json.load(f)
        return f"Available Inventory: {json.dumps(data)}"
    except Exception as e:
        return f"Error reading car database: {e}"

@tool("book_test_drive")
def book_test_drive(model: str, date: str, time: str) -> str:
    """
    Final step tool. Use ONLY when model, date, and time are all provided by the user.
    Args:
        model: The validated car model name.
        date: YYYY-MM-DD.
        time: HH:MM format.
    """
    try:
        booking_id = datetime.now().strftime("%H%M%S")
        confirmation = f"Booking confirmed for {model} on {date} at {time}. Ref: BK-{booking_id}."
        
        os.makedirs("logs", exist_ok=True)
        with open("logs/bookings.txt", "a") as f:
            f.write(f"{datetime.now()}: {confirmation}\n")

        return confirmation
    except Exception as e:
        return f"Booking failed: {str(e)}"