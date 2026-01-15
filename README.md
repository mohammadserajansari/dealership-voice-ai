# 🚗 Dealership Voice AI Assistant

An intelligent, voice-activated dealership receptionist powered by **CrewAI**, **Groq**, and **Deepgram**. This agent handles customer inquiries about car inventory (SUV/Sedan) from a local JSON database and manages test drive bookings through a natural voice interface.



## 🌟 Features
* **Voice-to-Voice Interaction:** Low-latency transcription and synthesis using Deepgram Nova-2 and Aura.
* **Inventory Intelligence:** Agent queries `cars.json` to provide real-time availability of models and variants.
* **Smart Scheduling:** Normalizes natural language dates (e.g., "next Tuesday") and checks for booking conflicts in SQLite.
* **Time-Aware Greetings:** Automatically greets users with "Good Morning," "Good Afternoon," or "Good Evening" based on the time of day.

### 📁 Project Structure
```Plaintext
├── agents
│   ├── factory.py         # CrewAI workflow & Agent logic
│   ├── receptionist.py    # Agent definitions & Pydantic schemas
│   └── voice_service.py   # Deepgram STT/TTS & Speech cleaning
├── data
│   └── cars.json          # Car inventory (SUV, Sedan, etc.)
├── database
│   └── database.py        # SQLite booking & session management
├── static
│   └── index.html         # Frontend Web Interface
├── tools
│   ├── search_tool.py     # Inventory & Booking tools
│   └── booking_tool.py    # Legacy booking logic
├── utils
│   └── scheduler.py       # Date/Time normalization logic
├── app.py                 # FastAPI Main Entry Point
├── docker-compose.yml     # Docker orchestration
├── .env                   # Environment variables (External)
└── requirements.txt       # Project dependencies
```

---

## 🛠️ Tech Stack
* **LLM Orchestration:** [CrewAI](https://crewai.com)
* **Inference:** [Groq](https://groq.com) (Llama-3 models)
* **STT/TTS:** [Deepgram](https://deepgram.com)
* **Backend:** [FastAPI](https://fastapi.tiangolo.com)
* **Database:** SQLite3

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the Repository
```bash
git clone "[https://github.com/mohammadserajansari/dealership-voice-ai.git](https://github.com/mohammadserajansari/dealership-voice-ai.git)"
cd dealership-voice-ai
```
### 2. Environment Setup
Create a .env file in the root directory and add your credentials:

```bash
GROQ_API_KEY=your_groq_key
DEEPGRAM_API_KEY=your_deepgram_key
MODEL_NAME=llama3-8b-8192
```
### 3. Install Dependencies
It is recommended to use Python 3.11:

```bash
# Create a virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```
###
4. Run the Application
```bash
uvicorn app:app --reload
```

### 5. Access the UI
Look into the static folder and open the index.html file in your preferred web browser to start the voice chat.
Note: Ensure your browser has microphone permissions enabled.

### 🐳 Docker Deployment
The project is containerized with Docker and Docker Compose for easy deployment, including the frontend.

Build and Start
```bash
docker-compose up --build
```
Run in Background
```bash

docker-compose up -d
```

### 📝 Usage Notes
Booking Validation: The agent will not book a car unless it exists in data/cars.json.

Booking Logs: All confirmed test drives are saved in bookings.db and logged in logs/bookings.txt.

Speech Formatting: The system uses <speech> tags to separate internal AI reasoning from spoken output, ensuring a clean voice experience.


Developed with by [Mohammad Seraj](https://www.linkedin.com/in/ansariserajmd/)