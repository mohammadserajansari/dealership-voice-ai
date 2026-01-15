# import re
# from datetime import datetime, timedelta,timezone

# import sqlite3

# DB_PATH = "bookings.db"

# NUMBER_WORDS = {
#     "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
#     "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
# }

# # -----------------------------
# # DATE NORMALIZATION
# # -----------------------------
# def normalize_date(text: str) -> str:
#     text = text.lower().strip()
#     # today = datetime.utcnow().date()
#     # current UTC datetime (timezone aware)
#     now_utc = datetime.now(timezone.utc)

#     # just the date portion
#     today = now_utc.date()

#     if text in ["today"]:
#         return today.isoformat()

#     if text in ["tomorrow", "tmr", "tmrw"]:
#         return (today + timedelta(days=1)).isoformat()

#     # after two / after 2
#     m = re.search(r"after (\w+)", text)
#     if m:
#         val = m.group(1)
#         days = NUMBER_WORDS.get(val, int(val) if val.isdigit() else None)
#         return (today + timedelta(days=days + 1)).isoformat()

#     # in three days
#     m = re.search(r"in (\w+)", text)
#     if m:
#         val = m.group(1)
#         days = NUMBER_WORDS.get(val, int(val) if val.isdigit() else None)
#         return (today + timedelta(days=days)).isoformat()

#     # Jan 16 / January 16
#     for fmt in ("%B %d", "%b %d"):
#         try:
#             return datetime.strptime(text, fmt).replace(year=today.year).date().isoformat()
#         except:
#             pass

#     # 2026-01-16
#     try:
#         return datetime.fromisoformat(text).date().isoformat()
#     except:
#         raise ValueError("Invalid date format")
    

# # -----------------------------
# # TIME NORMALIZATION
# # -----------------------------
# def normalize_time(text: str) -> str:
#     text = text.lower().replace(".", "").strip()

#     # 1pm / 1:30pm
#     m = re.match(r"(\d{1,2})(:(\d{2}))?\s*(am|pm)", text)
#     if m:
#         hour = int(m.group(1))
#         minute = int(m.group(3) or 0)
#         meridian = m.group(4)

#         if meridian == "pm" and hour != 12:
#             hour += 12
#         if meridian == "am" and hour == 12:
#             hour = 0

#         return f"{hour:02d}:{minute:02d}"

#     # 13:00
#     try:
#         t = datetime.strptime(text, "%H:%M")
#         return t.strftime("%H:%M")
#     except:
#         raise ValueError("Invalid time format")


# # -----------------------------
# # CONFLICT CHECK
# # -----------------------------
# def slot_available(model: str, date: str, time: str) -> bool:
#     with sqlite3.connect(DB_PATH) as conn:
#         cur = conn.cursor()
#         cur.execute(
#             "SELECT COUNT(*) FROM bookings WHERE model=? AND date=? AND time=?",
#             (model, date, time),
#         )
#         return cur.fetchone()[0] == 0


# def next_available_slot(model: str, date: str, time: str) -> str:
#     hour, minute = map(int, time.split(":"))
#     for _ in range(6):  # next 6 half-hour slots
#         minute += 30
#         if minute >= 60:
#             minute -= 60
#             hour += 1
#         new_time = f"{hour:02d}:{minute:02d}"

#         if slot_available(model, date, new_time):
#             return new_time

#     return None


########### try 5

import re
from datetime import datetime, timedelta, timezone
import sqlite3

DB_PATH = "bookings.db"

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6
}

# -----------------------------
# DATE NORMALIZATION
# -----------------------------
def normalize_date(text: str) -> str:
    text = text.lower().strip()
    now_utc = datetime.now(timezone.utc)
    today = now_utc.date()

    if text in ["today"]:
        return today.isoformat()
    if text in ["tomorrow", "tmr", "tmrw"]:
        return (today + timedelta(days=1)).isoformat()

    # in X days / after X days
    m = re.search(r"(?:in|after)\s+(\w+)", text)
    if m:
        val = m.group(1)
        days = NUMBER_WORDS.get(val, int(val) if val.isdigit() else None)
        if days is not None:
            offset = days if "in" in text else days + 1
            return (today + timedelta(days=offset)).isoformat()

    # before / after Xth of month
    m = re.search(r"(before|after)\s+(\d{1,2})(?:th|st|nd|rd)?", text)
    if m:
        direction, day = m.groups()
        day = int(day)
        try:
            target_date = today.replace(day=day)
        except ValueError:
            next_month = today.replace(day=1) + timedelta(days=32)
            target_date = next_month.replace(day=min(day, 28))
        if direction == "before":
            return (target_date - timedelta(days=1)).isoformat()
        else:
            return (target_date + timedelta(days=1)).isoformat()

    # weekday handling: next Monday / this Friday
    m = re.search(r"(next|this)?\s*(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", text)
    if m:
        prefix, day_name = m.groups()
        target_wd = WEEKDAYS[day_name]
        delta_days = (target_wd - today.weekday()) % 7
        if prefix == "next" or (prefix is None and delta_days == 0):
            delta_days += 7
        return (today + timedelta(days=delta_days)).isoformat()

    # Specific month/day: Jan 16 / January 16
    for fmt in ("%B %d", "%b %d"):
        try:
            return datetime.strptime(text, fmt).replace(year=today.year).date().isoformat()
        except:
            continue

    # ISO format
    try:
        return datetime.fromisoformat(text).date().isoformat()
    except:
        raise ValueError(f"Invalid date format: {text}")


# -----------------------------
# TIME NORMALIZATION
# -----------------------------
def normalize_time(text: str) -> str:
    text = text.lower().replace(".", "").strip()

    # 1pm / 1:30pm
    m = re.match(r"(\d{1,2})(:(\d{2}))?\s*(am|pm)", text)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(3) or 0)
        meridian = m.group(4)
        if meridian == "pm" and hour != 12:
            hour += 12
        if meridian == "am" and hour == 12:
            hour = 0
        return f"{hour:02d}:{minute:02d}"

    # 24h format
    try:
        t = datetime.strptime(text, "%H:%M")
        return t.strftime("%H:%M")
    except:
        pass

    # relative slots
    slots = {"morning": "09:00", "afternoon": "14:00", "evening": "17:00"}
    if text in slots:
        return slots[text]

    raise ValueError(f"Invalid time format: {text}")


# -----------------------------
# CONFLICT CHECK
# -----------------------------
def slot_available(model: str, date: str, time: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM bookings WHERE model=? AND date=? AND time=?",
            (model, date, time),
        )
        return cur.fetchone()[0] == 0


def next_available_slots(model: str, date: str, time: str, n=3) -> list:
    """Return next `n` available half-hour slots"""
    hour, minute = map(int, time.split(":"))
    slots = []
    for _ in range(24):  # check next 12 hours in 30-min increments
        minute += 30
        if minute >= 60:
            minute -= 60
            hour += 1
        if hour >= 20:  # closing time 8 PM
            break
        new_time = f"{hour:02d}:{minute:02d}"
        if slot_available(model, date, new_time):
            slots.append(new_time)
            if len(slots) >= n:
                break
    return slots
