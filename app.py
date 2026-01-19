import uuid
import logging
from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database.database import init_db, get_session_memory, save_session_memory
from agents.voice_service import transcribe_audio, process_crew_logic, generate_voice_response


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


init_db()

@app.post("/voice_chat")
async def voice_chat(file: UploadFile = File(...), x_session_id: str = Header(None)):
    try:
        session_id = x_session_id or str(uuid.uuid4())
        

        session = get_session_memory(session_id)
        

        audio_data = await file.read()
        user_text = await transcribe_audio(audio_data)
        

        reply = process_crew_logic(user_text, session["history"])
        

        new_history = session["history"] + f"\nUser: {user_text}\nAssistant: {reply}"
        save_session_memory(session_id, new_history)
        

        return generate_voice_response(reply, session_id, user_text)

    except Exception as e:
        logger.exception(f"Voice Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

