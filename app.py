########  working but token limit

# from fastapi import FastAPI, UploadFile, File, Header, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from datetime import datetime
# import uuid, json, base64, sqlite3, logging, re

# from deepgram import DeepgramClient
# from config import Config
# from agents.factory import DealershipCrew
# from schemas.schemas import BookingToolCall
# from utils.scheduler import normalize_date, normalize_time, slot_available, next_available_slots

# # -------------------------------
# # Logging & Config
# # -------------------------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI(title="Auto Dealership Voice AI")
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# dg = DeepgramClient(api_key=Config.DEEPGRAM_API_KEY)
# crew = DealershipCrew()

# DB_PATH = "bookings.db"

# # -------------------------------
# # Database Initialization
# # -------------------------------
# def init_db():
#     with sqlite3.connect(DB_PATH) as conn:
#         # Bookings Table
#         conn.execute("""
#             CREATE TABLE IF NOT EXISTS bookings (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 model TEXT, date TEXT, time TEXT, created_at TEXT
#             )
#         """)
#         # Persistent Memory Table
#         conn.execute("""
#             CREATE TABLE IF NOT EXISTS sessions (
#                 session_id TEXT PRIMARY KEY,
#                 history TEXT,
#                 pending_data TEXT
#             )
#         """)
#         conn.commit()

# init_db()

# # -------------------------------
# # Memory Management Helpers
# # -------------------------------
# def get_session_memory(session_id):
#     with sqlite3.connect(DB_PATH) as conn:
#         row = conn.execute(
#             "SELECT history, pending_data FROM sessions WHERE session_id = ?", 
#             (session_id,)
#         ).fetchone()
#         if row:
#             return {
#                 "history": row[0] or "", 
#                 "pending": json.loads(row[1]) if row[1] else None
#             }
#     return {"history": "", "pending": None}

# def save_session_memory(session_id, history, pending=None):
#     # Truncate history to last 10 lines to manage token limits
#     lines = history.strip().split("\n")
#     truncated_history = "\n".join(lines[-10:])
    
#     pending_json = json.dumps(pending) if pending else None
    
#     with sqlite3.connect(DB_PATH) as conn:
#         conn.execute("""
#             INSERT INTO sessions (session_id, history, pending_data)
#             VALUES (?, ?, ?)
#             ON CONFLICT(session_id) DO UPDATE SET
#                 history = excluded.history,
#                 pending_data = excluded.pending_data
#         """, (session_id, truncated_history, pending_json))
#         conn.commit()

# # -------------------------------
# # Booking Engine
# # -------------------------------
# def execute_booking(tool_call: BookingToolCall, session_id: str):
#     models = [m.strip() for m in tool_call.arguments.model.split(",")]
#     date = normalize_date(tool_call.arguments.date)
#     time_slot = normalize_time(tool_call.arguments.time)

#     responses = []
#     final_pending = None

#     for model in models:
#         if not slot_available(model, date, time_slot):
#             slots = next_available_slots(model, date, time_slot, 3)
#             if slots:
#                 # Store pending state to be saved in DB later
#                 final_pending = {"model": model, "date": date, "slots": slots}
#                 responses.append(
#                     f"{model} at {time_slot} is booked. Next available: {', '.join(slots)}. Should I book the earliest?"
#                 )
#             else:
#                 responses.append(f"Sorry, {model} has no availability on {date}.")
#             continue

#         with sqlite3.connect(DB_PATH) as conn:
#             cur = conn.cursor()
#             cur.execute(
#                 "INSERT INTO bookings (model, date, time, created_at) VALUES (?,?,?,?)",
#                 (model, date, time_slot, datetime.utcnow().isoformat())
#             )
#             conn.commit()
#             responses.append(f"Confirmed! Your {model} test drive is set for {date} at {time_slot}. Ref: {cur.lastrowid}.")

#     return " ".join(responses), final_pending

# # -------------------------------
# # Voice Endpoint
# # -------------------------------
# CONFIRM_WORDS = ["yes", "yeah", "yep", "sure", "ok", "go ahead"]
# CANCEL_WORDS = ["cancel", "abort", "stop", "forget it"]

# def clean_speech(raw):
#     matches = re.findall(r"<speech>(.*?)</speech>", raw, re.DOTALL)
#     return " ".join(m.strip() for m in matches) if matches else raw

# @app.post("/voice_chat")
# async def voice_chat(file: UploadFile = File(...), x_session_id: str = Header(None)):
#     try:
#         if not x_session_id:
#             x_session_id = str(uuid.uuid4())

#         # 1. Load Memory
#         session = get_session_memory(x_session_id)
#         history = session["history"]
#         pending = session["pending"]

#         # 2. STT
#         audio = await file.read()
#         stt = dg.listen.v1.media.transcribe_file(request=audio, model="nova-2", language="en-US")
#         user_text = stt.results.channels[0].alternatives[0].transcript.strip()
        
#         if not user_text:
#             return speak("I'm sorry, I didn't hear anything.", x_session_id)

#         # 3. Quick Logic: Confirmation of Pending Slot
#         if pending and any(w in user_text.lower() for w in CONFIRM_WORDS):
#             tool = BookingToolCall(
#                 tool="book_test_drive",
#                 arguments={"model": pending["model"], "date": pending["date"], "time": pending["slots"][0]}
#             )
#             reply, _ = execute_booking(tool, x_session_id)
#             new_history = history + f"User: {user_text}\nAssistant: {reply}\n"
#             save_session_memory(x_session_id, new_history, None)
#             return speak(reply, x_session_id)

#         # 4. LLM Workflow
#         prompt = f"{history}\nUser: {user_text}\nAssistant:"
#         result = crew.run_workflow(prompt)
#         raw_output = result.raw.strip()

#         # 5. Handle Tool Call vs. Speech
#         new_pending = None
#         if raw_output.startswith("{"):
#             parsed = json.loads(raw_output)
#             tool = BookingToolCall.model_validate(parsed)
#             reply, new_pending = execute_booking(tool, x_session_id)
#         else:
#             reply = clean_speech(raw_output)

#         # 6. Save Updated History & Pending State
#         updated_history = history + f"User: {user_text}\nAssistant: {reply}\n"
#         save_session_memory(x_session_id, updated_history, new_pending)

#         return speak(reply, x_session_id)

#     except Exception as e:
#         logger.exception(e)
#         raise HTTPException(500, str(e))


    
# def speak(text, sid, user_text=""):
#     out = f"{sid}.mp3"
#     with open(out, "wb") as f:
#         for c in dg.speak.v1.audio.generate(text=text, model="aura-2-thalia-en"):
#             f.write(c)

#     return FileResponse(
#         out,
#         media_type="audio/mpeg",
#         headers={
#             "X-Session-ID": sid,
#             "X-Transcript": base64.b64encode(text.encode()).decode(),
#             "X-User-Transcript": base64.b64encode(user_text.encode()).decode() # NEW
#         }
#     )

# @app.post("/reset_session")
# async def reset_session(x_session_id: str = Header(None)):
#     if not x_session_id:
#         return {"status": "no session to reset"}
    
#     with sqlite3.connect(DB_PATH) as conn:
#         # We clear history and pending_data but keep the record so the ID remains valid
#         conn.execute(
#             "UPDATE sessions SET history = '', pending_data = NULL WHERE session_id = ?", 
#             (x_session_id,)
#         )
#         conn.commit()
    
#     logger.info(f"[{x_session_id}] Session memory wiped.")
#     return {"status": "success", "message": "Memory cleared"}



############ try 23

# import os
# from deepgram import DeepgramClient
# from fastapi import FastAPI, UploadFile, File, Header, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
# from datetime import datetime
# import uuid, json, base64, sqlite3, logging, re, time, io
# import wave
# import httpx
# from config import Config
# from agents.factory import DealershipCrew
# from schemas.schemas import BookingToolCall
# from utils.scheduler import normalize_date, normalize_time, slot_available, next_available_slots

# # Setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# app = FastAPI(title="Auto Dealership Voice AI")
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# dg = DeepgramClient(api_key=Config.DEEPGRAM_API_KEY)
# crew = DealershipCrew()
# DB_PATH = "bookings.db"


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["X-Session-ID", "X-Transcript", "X-User-Transcript"] # ADD THIS LINE
# )
# # -------------------------------
# # Database & Memory Logic
# # -------------------------------
# def init_db():
#     with sqlite3.connect(DB_PATH) as conn:
#         conn.execute("CREATE TABLE IF NOT EXISTS bookings (id INTEGER PRIMARY KEY AUTOINCREMENT, model TEXT, date TEXT, time TEXT, created_at TEXT)")
#         conn.execute("CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, history TEXT, pending_data TEXT)")
#         conn.commit()

# init_db()

# def get_session_memory(session_id):
#     with sqlite3.connect(DB_PATH) as conn:
#         row = conn.execute("SELECT history, pending_data FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
#         return {"history": row[0] or "", "pending": json.loads(row[1]) if row[1] else None} if row else {"history": "", "pending": None}

# def save_session_memory(session_id, history, pending=None):
#     # Truncate history to last 8 lines to save tokens
#     truncated_history = "\n".join(history.strip().split("\n")[-8:])
#     pending_json = json.dumps(pending) if pending else None
#     with sqlite3.connect(DB_PATH) as conn:
#         conn.execute("INSERT INTO sessions (session_id, history, pending_data) VALUES (?, ?, ?) ON CONFLICT(session_id) DO UPDATE SET history = excluded.history, pending_data = excluded.pending_data", (session_id, truncated_history, pending_json))
#         conn.commit()

# # -------------------------------
# # Booking Execution
# # -------------------------------
# def execute_booking(tool_call: BookingToolCall):
#     model = tool_call.arguments.model
#     date = normalize_date(tool_call.arguments.date)
#     time_slot = normalize_time(tool_call.arguments.time)

#     if not slot_available(model, date, time_slot):
#         slots = next_available_slots(model, date, time_slot, 3)
#         return f"Sorry, {model} is unavailable at {time_slot}. Next available: {', '.join(slots)}.", {"model": model, "date": date, "slots": slots}

#     with sqlite3.connect(DB_PATH) as conn:
#         cur = conn.cursor()
#         cur.execute("INSERT INTO bookings (model, date, time, created_at) VALUES (?,?,?,?)", (model, date, time_slot, datetime.utcnow().isoformat()))
#         conn.commit()
#     return f"Confirmed! Your {model} test drive is set for {date} at {time_slot}. Ref: {cur.lastrowid}.", None

# def clean_speech(raw):
#     matches = re.findall(r"<speech>(.*?)</speech>", raw, re.DOTALL)
#     return " ".join(m.strip() for m in matches) if matches else raw

# @app.post("/voice_chat")
# async def voice_chat(file: UploadFile = File(...), x_session_id: str = Header(None)):
#     try:
#         if not x_session_id:
#             x_session_id = str(uuid.uuid4())

#         session = get_session_memory(x_session_id)
#         history, pending = session["history"], session["pending"]

#         audio_data = await file.read()
        
#         # Matching your working CURL command
#         import httpx
#         async with httpx.AsyncClient() as client:
#             stt_res = await client.post(
#                 "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true",
#                 headers={
#                     "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
#                     "Content-Type": "audio/wav" # Explicitly set content type
#                 },
#                 content=audio_data
#             )
            
#             if stt_res.status_code != 200:
#                 raise Exception(f"Deepgram STT error: {stt_res.text}")
            
#             stt_json = stt_res.json()
#             user_text = stt_json['results']['channels'][0]['alternatives'][0]['transcript'].strip()

#         # ... (Rest of your CrewAI logic remains the same)
#         result = crew.run_workflow(user_text, chat_history=history)
#         reply = clean_speech(str(result.raw))

#         save_session_memory(x_session_id, history + f"\nUser: {user_text}\nAssistant: {reply}")
#         return speak(reply, x_session_id, user_text)

#     except Exception as e:
#         logger.exception(f"Voice Chat Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


    
# def speak(text, sid, user_text=""):
#     try:
#         import httpx
        
#         # We use aura-luna-en as it is usually the default available model
#         payload = {"text": text}
#         params = {
#             "model": "aura-luna-en", 
#             "encoding": "linear16",
#             "container": "wav",
#             "sample_rate": 16000
#         }
        
#         with httpx.Client() as client:
#             response = client.post(
#                 "https://api.deepgram.com/v1/speak",
#                 params=params,
#                 headers={
#                     "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
#                     "Content-Type": "application/json"
#                 },
#                 json=payload
#             )
            
#             # If still forbidden, your project might not have TTS enabled at all
#             if response.status_code != 200:
#                 logger.error(f"Deepgram TTS API Error: {response.text}")
#                 # Return empty audio so the frontend doesn't break
#                 return StreamingResponse(io.BytesIO(b""), media_type="audio/wav")

#             audio_buffer = io.BytesIO(response.content)
#             audio_buffer.seek(0)

#         return StreamingResponse(
#             audio_buffer,
#             media_type="audio/wav",
#             headers={
#                 "X-Session-ID": str(sid),
#                 "X-Transcript": base64.b64encode(text.encode()).decode(),
#                 "X-User-Transcript": base64.b64encode(user_text.encode()).decode(),
#                 "Access-Control-Expose-Headers": "X-Session-ID, X-Transcript, X-User-Transcript"
#             }
#         )
#     except Exception as e:
#         logger.error(f"TTS Error: {e}")
#         return StreamingResponse(io.BytesIO(b""), media_type="audio/wav")





#################


import uuid
import logging
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Internal Imports
from database.database import init_db, get_session_memory, save_session_memory
from agents.voice_service import transcribe_audio, process_crew_logic, generate_voice_response

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auto Dealership Voice AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-ID", "X-Transcript", "X-User-Transcript"]
)

# Initialize DB on startup
init_db()

@app.post("/voice_chat")
async def voice_chat(file: UploadFile = File(...), x_session_id: str = Header(None)):
    try:
        session_id = x_session_id or str(uuid.uuid4())
        
        # 1. Get Memory
        session = get_session_memory(session_id)
        
        # 2. Transcribe
        audio_data = await file.read()
        user_text = await transcribe_audio(audio_data)
        
        # 3. Process with CrewAI
        reply = process_crew_logic(user_text, session["history"])
        
        # 4. Save Memory
        new_history = session["history"] + f"\nUser: {user_text}\nAssistant: {reply}"
        save_session_memory(session_id, new_history)
        
        # 5. Return Audio Stream
        return generate_voice_response(reply, session_id, user_text)

    except Exception as e:
        logger.exception(f"Voice Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)