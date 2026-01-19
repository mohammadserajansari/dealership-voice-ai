# import os
# import httpx
# import re
# import io
# import base64
# from fastapi.responses import StreamingResponse
# from config import Config
# from agents.factory import DealershipCrew


# crew = DealershipCrew()

# async def transcribe_audio(audio_data: bytes):
#     async with httpx.AsyncClient() as client:
#         res = await client.post(
#             "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true",
#             headers={
#                 "Authorization": f"Token {Config.DEEPGRAM_API_KEY}",
#                 "Content-Type": "audio/wav"
#             },
#             content=audio_data
#         )
#         if res.status_code != 200:
#             raise Exception(f"Deepgram STT error: {res.text}")
#         return res.json()['results']['channels'][0]['alternatives'][0]['transcript'].strip()

# def clean_speech(raw_text: str):
#     """
#     Extracts speech from tags. If no tags found, cleans up technical 
#     characters to make the raw text readable for TTS.
#     """

#     matches = re.findall(r"<speech>(.*?)</speech>", raw_text, re.DOTALL)
#     if matches:
#         return " ".join(m.strip() for m in matches)
    


#     clean = re.sub(r"[`*#_]", "", raw_text)  
#     clean = re.sub(r"\{.*?\}", "", clean)    
#     clean = clean.replace("SUCCESS:", "Success.")
#     clean = clean.replace("BK-", "Booking reference ")
    
#     # Trim excessive whitespace
#     clean = " ".join(clean.split())
    
#     return clean if clean else "I'm sorry, I encountered an error. How can I help you today?"

# def generate_voice_response(text, sid, user_text=""):

#     if not text.strip():
#         text = "I'm listening. Please go ahead."

#     payload = {"text": text}
#     params = {
#         "model": "aura-luna-en", 
#         "encoding": "linear16", 
#         "container": "wav", 
#         "sample_rate": 16000
#     }
    
#     with httpx.Client() as client:
#         response = client.post(
#             "https://api.deepgram.com/v1/speak",
#             params=params,
#             headers={
#                 "Authorization": f"Token {Config.DEEPGRAM_API_KEY}", 
#                 "Content-Type": "application/json"
#             },
#             json=payload
#         )
        
#         audio_content = response.content if response.status_code == 200 else b""
#         audio_buffer = io.BytesIO(audio_content)
#         audio_buffer.seek(0)

#     return StreamingResponse(
#         audio_buffer,
#         media_type="audio/wav",
#         headers={
#             "X-Session-ID": str(sid),
#             "X-Transcript": base64.b64encode(text.encode()).decode(),
#             "X-User-Transcript": base64.b64encode(user_text.encode()).decode(),
#             "Access-Control-Expose-Headers": "X-Session-ID, X-Transcript, X-User-Transcript"
#         }
#     )

# def process_crew_logic(user_text, history):

#     result = crew.run_workflow(user_text, chat_history=history)
    

#     raw_output = str(result.raw)
#     return clean_speech(raw_output)




import os
import httpx
import re
import io
import base64
import logging
from fastapi.responses import StreamingResponse
from config import Config
from agents.factory import DealershipCrew

# Setup logging
logger = logging.getLogger("voice_service")
crew = DealershipCrew()

# Define a global timeout configuration for all external calls
# 15s to connect, 60s total for the operation
GLOBAL_TIMEOUT = httpx.Timeout(60.0, connect=15.0)

async def transcribe_audio(audio_data: bytes):
    """Transcribe user audio with robust timeout protection."""
    async with httpx.AsyncClient(timeout=GLOBAL_TIMEOUT) as client:
        try:
            res = await client.post(
                "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true",
                headers={
                    "Authorization": f"Token {Config.DEEPGRAM_API_KEY}",
                    "Content-Type": "audio/wav"
                },
                content=audio_data
            )
            
            if res.status_code != 200:
                logger.error(f"Deepgram STT Error: {res.status_code} - {res.text}")
                return "Error: Could not transcribe audio."
                
            data = res.json()
            return data['results']['channels'][0]['alternatives'][0]['transcript'].strip()
            
        except httpx.ConnectTimeout:
            logger.error("Connection to Deepgram timed out during transcription.")
            return "Error: Transcription connection timeout."
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return ""

def clean_speech(raw_text: str):
    """Extracts and cleans text for the TTS engine."""
    matches = re.findall(r"<speech>(.*?)</speech>", raw_text, re.DOTALL)
    if matches:
        return " ".join(m.strip() for m in matches)
    
    # Fallback cleaning if tags are missing
    clean = re.sub(r"[`*#_]", "", raw_text)  
    clean = re.sub(r"\{.*?\}", "", clean)    
    clean = clean.replace("SUCCESS:", "Success.")
    clean = clean.replace("BK-", "Booking reference ")
    
    clean = " ".join(clean.split())
    return clean if clean else "I'm listening. How can I help?"

def generate_voice_response(text, sid, user_text=""):
    """Generate audio stream with timeout protection and fallback audio."""
    if not text.strip():
        text = "I'm listening. Please go ahead."

    payload = {"text": text}
    params = {
        "model": "aura-luna-en", 
        "encoding": "linear16", 
        "container": "wav", 
        "sample_rate": 16000
    }
    
    # We use a standard Client here as it's called within a non-async context usually
    with httpx.Client(timeout=GLOBAL_TIMEOUT) as client:
        try:
            response = client.post(
                "https://api.deepgram.com/v1/speak",
                params=params,
                headers={
                    "Authorization": f"Token {Config.DEEPGRAM_API_KEY}", 
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            if response.status_code == 200:
                audio_content = response.content
            else:
                logger.error(f"Deepgram TTS Error: {response.status_code}")
                audio_content = b"" # Fallback to empty if failed
                
        except (httpx.ConnectTimeout, httpx.ReadTimeout):
            logger.error("Deepgram TTS timed out.")
            audio_content = b""
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            audio_content = b""

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
    """Runs the CrewAI workflow and cleans the output."""
    try:
        result = crew.run_workflow(user_text, chat_history=history)
        raw_output = str(result.raw)
        return clean_speech(raw_output)
    except Exception as e:
        logger.error(f"CrewAI Logic Error: {e}")
        return "I'm sorry, I'm having trouble processing that right now. Could you please repeat?"