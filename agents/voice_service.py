import os
import httpx
import re
import io
import base64
from fastapi.responses import StreamingResponse
from config import Config
from agents.factory import DealershipCrew

# Initialize the crew
crew = DealershipCrew()

async def transcribe_audio(audio_data: bytes):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true",
            headers={
                "Authorization": f"Token {Config.DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            },
            content=audio_data
        )
        if res.status_code != 200:
            raise Exception(f"Deepgram STT error: {res.text}")
        return res.json()['results']['channels'][0]['alternatives'][0]['transcript'].strip()

def clean_speech(raw_text: str):
    """
    Extracts speech from tags. If no tags found, cleans up technical 
    characters to make the raw text readable for TTS.
    """
    # 1. Try to find content inside <speech> tags
    matches = re.findall(r"<speech>(.*?)</speech>", raw_text, re.DOTALL)
    if matches:
        return " ".join(m.strip() for m in matches)
    
    # 2. Fallback: If no tags, clean up the raw output for voice
    # Remove common AI "thought" artifacts or markdown
    clean = re.sub(r"[`*#_]", "", raw_text)  # Remove markdown bold/italic/code
    clean = re.sub(r"\{.*?\}", "", clean)    # Remove JSON-like curly braces
    clean = clean.replace("SUCCESS:", "Success.")
    clean = clean.replace("BK-", "Booking reference ")
    
    # Trim excessive whitespace
    clean = " ".join(clean.split())
    
    return clean if clean else "I'm sorry, I encountered an error. How can I help you today?"

def generate_voice_response(text, sid, user_text=""):
    # Ensure text isn't empty for Deepgram
    if not text.strip():
        text = "I'm listening. Please go ahead."

    payload = {"text": text}
    params = {
        "model": "aura-luna-en", 
        "encoding": "linear16", 
        "container": "wav", 
        "sample_rate": 16000
    }
    
    with httpx.Client() as client:
        response = client.post(
            "https://api.deepgram.com/v1/speak",
            params=params,
            headers={
                "Authorization": f"Token {Config.DEEPGRAM_API_KEY}", 
                "Content-Type": "application/json"
            },
            json=payload
        )
        
        audio_content = response.content if response.status_code == 200 else b""
        audio_buffer = io.BytesIO(audio_content)
        audio_buffer.seek(0)

    return StreamingResponse(
        audio_buffer,
        media_type="audio/wav",
        headers={
            "X-Session-ID": str(sid),
            "X-Transcript": base64.b64encode(text.encode()).decode(),
            "X-User-Transcript": base64.b64encode(user_text.encode()).decode(),
            "Access-Control-Expose-Headers": "X-Session-ID, X-Transcript, X-User-Transcript"
        }
    )

def process_crew_logic(user_text, history):
    # Kickoff the agent workflow
    result = crew.run_workflow(user_text, chat_history=history)
    
    # Convert CrewOutput to string and clean it
    raw_output = str(result.raw)
    return clean_speech(raw_output)