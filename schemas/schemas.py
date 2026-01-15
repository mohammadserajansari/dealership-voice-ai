# from pydantic import BaseModel

# class BookingArguments(BaseModel):
#     model: str
#     date: str
#     time: str

# class BookingToolCall(BaseModel):
#     tool: str
#     arguments: BookingArguments


from pydantic import BaseModel
from typing import Literal

class BookingArguments(BaseModel):
    model: str
    date: str
    time: str

class BookingToolCall(BaseModel):
    tool: Literal["book_test_drive"]
    arguments: BookingArguments
