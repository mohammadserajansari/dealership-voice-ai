from langchain.tools import tool
import json
import os
from datetime import datetime

class BookingTools:
    
    @tool("book_test_drive")
    def book_test_drive(booking_details: str):
        """
        Useful to book a test drive. 
        Input should be a JSON string with keys: 'model', 'date', and 'time'.
        Example: {"model": "X-Trail", "date": "2024-05-20", "time": "11:00 AM"}
        """
        try:
            # Parse the string input from the agent
            data = json.loads(booking_details)
            
            model = data.get("model")
            date = data.get("date")
            time = data.get("time")

            # In production, you would insert into a DB (PostgreSQL/MongoDB) 
            # or call the Google Calendar/Calendly API here.
            
            # For now, we simulate a successful database entry
            booking_id = f"BK-{datetime.now().strftime('%f')}"
            
            confirmation_message = (
                f"SUCCESS: Booking confirmed for {model}. "
                f"Reference ID: {booking_id}. "
                f"Scheduled for {date} at {time}."
            )
            
            # Log the booking locally for verification
            with open("logs/bookings.txt", "a") as f:
                f.write(f"{datetime.now()}: {confirmation_message}\n")
                
            return confirmation_message

        except Exception as e:
            return f"Error processing booking: {str(e)}. Please ensure model, date, and time are provided."