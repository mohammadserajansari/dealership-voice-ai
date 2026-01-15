# from crewai import Agent, Task, Crew, Process, LLM
# from config import Config
# from tools.search_tool import query_knowledge_base, book_test_drive
# from schemas.schemas import BookingToolCall


# class DealershipCrew:
#     def __init__(self):
#         self.llm = LLM(
#             model=Config.MODEL_NAME,          # e.g. llama-3.3-70b-versatile
#             api_key=Config.GROQ_TOKEN,
#             base_url="https://api.groq.com/openai/v1"
#         )

#     def _agent(self):
#         return Agent(
#             role="Receptionist",
#             goal="Understand customer intent and either ask questions or book test drives.",
#             backstory="You are a helpful car dealership receptionist.",
#             tools=[query_knowledge_base, book_test_drive],
#             llm=self.llm,
#             verbose=True,
#             allow_delegation=False
#         )

#     def run_workflow(self, user_input: str):
#         agent = self._agent()

#         prompt = f"""
# Customer: {user_input}

# You are a dealership receptionist.

# Rules:
# 1. If the customer asks about cars → call query_knowledge_base.
# 2. If the customer wants a test drive:
#    - Extract model, date, and time.
#    - If any are missing → ask a follow-up question.
# 3. When ALL details are known → RETURN ONLY valid JSON for BookingToolCall.

# The JSON MUST look exactly like:

# {{
#   "tool": "book_test_drive",
#   "arguments": {{
#     "model": "SUV",
#     "date": "2026-01-15",
#     "time": "10:00 AM"
#   }}
# }}

# Do NOT include thoughts, explanations, or extra text when returning JSON.
# """

#         task = Task(
#             description=prompt,
#             expected_output="Either a normal text reply OR a valid BookingToolCall JSON",
#             agent=agent,
#             output_pydantic=BookingToolCall
#         )

#         crew = Crew(
#             agents=[agent],
#             tasks=[task],
#             process=Process.sequential,
#             verbose=True
#         )

#         result = crew.kickoff()
#         return result


############## try 3


# from crewai import Agent, Task, Crew, Process, LLM
# from config import Config
# from tools.search_tool import query_knowledge_base, book_test_drive
# from schemas.schemas import BookingToolCall


# class DealershipCrew:
#     def __init__(self):
#         self.llm = LLM(
#             model=Config.MODEL_NAME,          
#             api_key=Config.GROQ_TOKEN,
#             base_url="https://api.groq.com/openai/v1"
#         )

#     def _agent(self):
#         return Agent(
#             role="Receptionist",
#             goal="Help customers with car inquiries and book test drives accurately.",
#             backstory=(
#                 "You are a professional dealership receptionist. You must communicate clearly. "
#                 "CRITICAL: Every time you speak to the customer, you MUST wrap your spoken words "
#                 "in <speech> tags. For example: <speech>Hello, how can I help you?</speech>. "
#                 "Do not include your internal thoughts or action descriptions inside the speech tags."
#             ),
#             tools=[query_knowledge_base, book_test_drive],
#             llm=self.llm,
#             verbose=True,
#             allow_delegation=False
#         )

#     def run_workflow(self, user_input: str):
#         agent = self._agent()

#         prompt = f"""
# Customer Input: {user_input}

# You are a dealership receptionist operating via a voice interface.

# STRICT OPERATING RULES:
# 1. INQUIRIES: If the customer asks about cars or availability, use the 'query_knowledge_base' tool. 
#    Then, respond to the customer using <speech>Your spoken answer here</speech>.

# 2. TEST DRIVES: 
#    - Extract the car model, date, and time.
#    - If information is missing, ask for it using <speech> tags. 
#    - Example: <speech>Which model were you interested in trying out?</speech>

# 3. FINAL BOOKING: When you have the model, date, and time, you must return ONLY the valid JSON for 'BookingToolCall'.
#    - DO NOT use <speech> tags when returning the JSON.
#    - DO NOT include 'Thought:' or any conversational text when providing the JSON.

# JSON FORMAT:
# {{
#   "tool": "book_test_drive",
#   "arguments": {{
#     "model": "SUV",
#     "date": "2026-01-15",
#     "time": "10:00 AM"
#   }}
# }}

# Remember: If you are talking, use <speech>...</speech>. If you are booking, return ONLY JSON.
# """

#         task = Task(
#             description=prompt,
#             expected_output="A response wrapped in <speech> tags OR a valid BookingToolCall JSON string.",
#             agent=agent
#         )

#         crew = Crew(
#             agents=[agent],
#             tasks=[task],
#             process=Process.sequential,
#             verbose=True
#         )

#         result = crew.kickoff()
#         return result


# ############# try 4

# # from crewai import Agent, Task, Crew, Process, LLM
# # from config import Config
# # from tools.search_tool import query_knowledge_base, book_test_drive
# # # We remove the hard Pydantic enforcement to allow for flexible speech/JSON output

# # class DealershipCrew:
# #     def __init__(self):
# #         self.llm = LLM(
# #             model=Config.MODEL_NAME,
# #             api_key=Config.GROQ_TOKEN,
# #             base_url="https://api.groq.com/openai/v1"
# #         )

# #     def _agent(self):
# #         return Agent(
# #             role="Receptionist",
# #             goal="Identify customer needs and book test drives.",
# #             backstory=(
# #                 "You are a professional dealership receptionist. "
# #                 "Whenever you want to say something to the customer, you MUST wrap it in <speech> tags. "
# #                 "If you are ready to book, you provide ONLY the JSON."
# #             ),
# #             tools=[query_knowledge_base, book_test_drive],
# #             llm=self.llm,
# #             verbose=True,
# #             allow_delegation=False
# #         )

# #     def run_workflow(self, user_input: str):
# #         agent = self._agent()

# #         # Simplified prompt to reduce LLM confusion
# #         prompt = f"""
# # User input: {user_input}

# # Instructions:
# # 1. If the user asks about cars: Use 'query_knowledge_base' then answer using <speech> tags.
# # 2. If the user wants to book:
# #    - You need: Model, Date, and Time.
# #    - If ANY are missing: Ask for them using <speech> tags.
# #    - If ALL are present: Return ONLY the JSON below.

# # JSON format for booking:
# # {{
# #   "tool": "book_test_drive",
# #   "arguments": {{
# #     "model": "CAR_MODEL",
# #     "date": "YYYY-MM-DD",
# #     "time": "HH:MM AM/PM"
# #   }}
# # }}

# # CRITICAL: Never use <speech> tags and JSON in the same response. Pick one.
# # """

# #         task = Task(
# #             description=prompt,
# #             expected_output="A <speech> tagged response OR a JSON booking object.",
# #             agent=agent
# #             # Removed output_pydantic to allow the agent to return speech text
# #         )

# #         crew = Crew(
# #             agents=[agent],
# #             tasks=[task],
# #             process=Process.sequential,
# #             verbose=True
# #         )

# #         result = crew.kickoff()
# #         return result


#### try 4


# from crewai import Agent, Task, Crew, Process, LLM
# from config import Config
# from tools.search_tool import query_knowledge_base, book_test_drive
# from schemas.schemas import BookingToolCall


# class DealershipCrew:
#     def __init__(self):
#         self.llm = LLM(
#             model=Config.MODEL_NAME,
#             api_key=Config.GROQ_TOKEN,
#             base_url="https://api.groq.com/openai/v1"
#         )

#     def _agent(self):
#         return Agent(
#             role="Receptionist",
#             goal="Help customers with car inquiries and book test drives accurately.",
#             backstory=(
#                 "You are a professional dealership receptionist. Always be helpful and concise. "
#                 "STRICT OUTPUT RULES:\n"
#                 "1. INTERNAL THOUGHTS: Use internal thoughts for reasoning but never speak them.\n"
#                 "2. SPEAKING: Wrap any customer-facing text in <speech> tags. Example: <speech>Hello!</speech>\n"
#                 "3. BOOKING: When you have car model, date, and time, return ONLY JSON for 'BookingToolCall'. "
#                 "Do not use <speech> tags for JSON.\n"
#                 "4. MISSING INFO: If any detail for booking is missing, ask the customer using <speech> tags.\n"
#                 "5. NEVER include 'Thought:' or 'Action:' in <speech>.\n"
#             ),
#             tools=[query_knowledge_base, book_test_drive],
#             llm=self.llm,
#             verbose=True,
#             allow_delegation=False
#         )

#     def run_workflow(self, user_input: str):
#         """
#         Runs a CrewAI workflow given user input.
#         Returns an object with `.raw` containing either:
#         - <speech>...<speech> response for the user, or
#         - JSON for BookingToolCall.
#         """
#         agent = self._agent()

#         prompt = f"""
# Customer Input: {user_input}

# You are a dealership receptionist operating via a voice interface.

# STRICT OPERATING RULES:
# 1. INQUIRIES:
#    - If the customer asks about cars or availability, use 'query_knowledge_base'.
#    - Respond to the customer using <speech>...</speech>.

# 2. TEST DRIVES:
#    - Extract the car model, date, and time.
#    - If any information is missing, ask for it using <speech> tags. 
#      Example: <speech>Which model were you interested in?</speech>

# 3. FINAL BOOKING:
#    - When you have model, date, and time, return ONLY a valid BookingToolCall JSON string.
#    - DO NOT use <speech> tags when returning JSON.
#    - DO NOT include 'Thought:' or extra conversation in JSON.

# JSON FORMAT:
# {{
#   "tool": "book_test_drive",
#   "arguments": {{
#     "model": "SUV",
#     "date": "2026-01-15",
#     "time": "10:00 AM"
#   }}
# }}

# Remember:
# - Use <speech>...</speech> for anything you want the user to hear.
# - Return ONLY JSON for confirmed bookings.
# - If any detail is missing, ask using <speech> tags.
# """

#         task = Task(
#             description=prompt,
#             expected_output="Either <speech>...</speech> or valid BookingToolCall JSON string",
#             agent=agent
#         )

#         crew = Crew(
#             agents=[agent],
#             tasks=[task],
#             process=Process.sequential,
#             verbose=True
#         )

#         result = crew.kickoff()
#         return result


######### try 5


# from crewai import Agent, Task, Crew, Process, LLM
# from config import Config
# from tools.search_tool import query_knowledge_base, book_test_drive
# from schemas.schemas import BookingToolCall
# from utils.scheduler import normalize_date, normalize_time

# class DealershipCrew:
#     def __init__(self):
#         self.llm = LLM(
#             model=Config.MODEL_NAME,
#             api_key=Config.GROQ_TOKEN,
#             base_url="https://api.groq.com/openai/v1"
#         )

#     def _agent(self):
#         return Agent(
#             role="Receptionist",
#             goal="Help customers with car inquiries and book test drives accurately.",
#             backstory=(
#                 "You are a professional dealership receptionist. Always be helpful and concise.\n\n"
#                 "STRICT OUTPUT RULES:\n"
#                 "1. INTERNAL THOUGHTS: You may think internally but NEVER put them in <speech>.\n"
#                 "2. SPEAKING: Wrap all customer-facing text in <speech> tags. Example:\n"
#                 "   Correct: <speech>Hello!</speech>\n"
#                 "   Incorrect: <speech>Thought: I think they want an SUV.</speech>\n"
#                 "3. BOOKING: Once you have model, date, and time, return ONLY JSON for 'BookingToolCall'.\n"
#                 "4. MISSING INFO: Ask the customer using <speech> tags if any detail is missing.\n"
#                 "5. NEVER include 'Thought:' or 'Action:' inside <speech>.\n"
#                 "6. Always respond concisely.\n"
#                 "7. JSON format:\n"
#                 "{\n"
#                 "  \"tool\": \"book_test_drive\",\n"
#                 "  \"arguments\": {\n"
#                 "    \"model\": \"SUV\",\n"
#                 "    \"date\": \"2026-01-15\",\n"
#                 "    \"time\": \"10:00 AM\"\n"
#                 "  }\n"
#                 "}"
#             ),
#             tools=[query_knowledge_base, book_test_drive],
#             llm=self.llm,
#             verbose=True,
#             allow_delegation=False
#         )

#     def run_workflow(self, user_input: str):
#         """
#         Runs a CrewAI workflow given user input.
#         Returns an object with `.raw` containing either:
#         - <speech>...</speech> response for the user
#         - JSON for BookingToolCall
#         """

#         # ------------------------
#         # Preprocess relative dates/times
#         # ------------------------
#         processed_input = user_input

#         # Look for patterns like "after X days", "before 20th", "tomorrow", "today"
#         try:
#             words = user_input.lower().split()
#             for i, w in enumerate(words):
#                 if w in ["today", "tomorrow", "tmr", "tmrw"] or w.startswith("after") or w.startswith("in") or w.startswith("before"):
#                     # Normalize date
#                     try:
#                         normalized = normalize_date(w + " " + " ".join(words[i+1:i+2]))  # include next word if exists
#                         processed_input = processed_input.replace(words[i], normalized)
#                     except:
#                         pass
#                 # Normalize time like "1pm", "13:30"
#                 if any(ampm in w for ampm in ["am", "pm"]) or ":" in w:
#                     try:
#                         normalized_time = normalize_time(w)
#                         processed_input = processed_input.replace(w, normalized_time)
#                     except:
#                         pass
#         except Exception as e:
#             # fallback: leave input as-is
#             processed_input = user_input

#         agent = self._agent()

#         prompt = f"""
# Customer Input: {processed_input}

# You are a dealership receptionist operating via a voice interface.

# REMEMBER:
# - Use <speech>...</speech> for all spoken messages to the customer.
# - NEVER include internal thoughts inside <speech>.
# - If booking is complete (model, date, time), return ONLY a valid JSON for BookingToolCall.
# - If any booking detail is missing, ask using <speech> tags.
# - Respond concisely and helpfully.

# JSON FORMAT:
# {{
#   "tool": "book_test_drive",
#   "arguments": {{
#     "model": "SUV",
#     "date": "2026-01-15",
#     "time": "10:00 AM"
#   }}
# }}
# """

#         task = Task(
#             description=prompt,
#             expected_output="Either <speech>...</speech> for user-facing text, or BookingToolCall JSON string",
#             agent=agent
#         )

#         crew = Crew(
#             agents=[agent],
#             tasks=[task],
#             process=Process.sequential,
#             verbose=True
#         )

#         result = crew.kickoff()
#         return result



###### try 6



# from crewai import Agent, Task, Crew, Process, LLM
# from config import Config
# from tools.search_tool import query_knowledge_base, book_test_drive
# from utils.scheduler import normalize_date, normalize_time
# from datetime import datetime

# class DealershipCrew:
#     def __init__(self):
#         self.llm = LLM(
#             model=Config.MODEL_NAME,
#             api_key=Config.GROQ_TOKEN,
#             base_url="https://api.groq.com/openai/v1",
#             temperature=0  # Set to 0 for better tool calling reliability
#         )

#     def _agent(self):
#         return Agent(
#             role="Receptionist",
#             goal="Collect car model, date, and time to book test drives using the available tools.",
#             backstory=(
#                 "You are a professional dealership receptionist. Your main job is to book test drives.\n\n"
#                 "CRITICAL RULES:\n"
#                 "1. If 'model', 'date', or 'time' is missing, ask for it using <speech> tags.\n"
#                 "2. As soon as you have all three pieces of information, you MUST call the 'book_test_drive' tool.\n"
#                 "3. After the tool executes, summarize the result for the customer in <speech> tags.\n"
#                 "4. NEVER explain your thoughts or tool steps inside <speech> tags.\n"
#                 "5. Only use <speech>...</speech> for talking. No other text format is allowed."
#             ),
#             tools=[query_knowledge_base, book_test_drive],
#             llm=self.llm,
#             verbose=True,
#             allow_delegation=False
#         )

#     def run_workflow(self, user_input: str):
#         """
#         Runs a CrewAI workflow. If the booking is triggered, the tool logic 
#         inside search_tool.py will handle the actual data saving.
#         """

#         # Preprocess relative dates/times
#         processed_input = user_input
#         current_date = datetime.now().strftime("%Y-%m-%d")

#         try:
#             words = user_input.lower().split()
#             for i, w in enumerate(words):
#                 if w in ["today", "tomorrow", "tmr", "tmrw"]:
#                     try:
#                         normalized = normalize_date(w)
#                         processed_input = processed_input.replace(w, normalized)
#                     except: pass
#                 if any(ampm in w for ampm in ["am", "pm"]) or ":" in w:
#                     try:
#                         normalized_time = normalize_time(w)
#                         processed_input = processed_input.replace(w, normalized_time)
#                     except: pass
#         except Exception:
#             processed_input = user_input

#         agent = self._agent()

#         # The prompt is now focused on the ACTION of booking rather than just returning JSON text
#         # prompt_description = f"""
#         # Today's date is {current_date}.
#         # Customer said: "{processed_input}"

#         # Task:
#         # 1. Identify if the customer wants to book a test drive.
#         # 2. If they haven't specified a car model, date, or time, ask them using <speech>.
#         # 3. If you have all details (Model, Date, and Time), immediately CALL the 'book_test_drive' tool.
#         # 4. Once the booking tool returns a success message, confirm it to the user in <speech>.
#         # """
#         # Instead of a giant multi-line string, keep it surgical:
#         prompt_description = f"Today: {current_date}. User: {processed_input}. Task: Book test drive if details present, else ask."

#         task = Task(
#             description=prompt_description,
#             expected_output="A <speech> tag containing either a question for missing info or a booking confirmation.",
#             agent=agent
#         )

#         crew = Crew(
#             agents=[agent],
#             tasks=[task],
#             process=Process.sequential,
#             verbose=True
#         )

#         result = crew.kickoff()
#         return result



# try 7



# from crewai import Agent, Task, Crew, Process, LLM
# from config import Config
# from tools.search_tool import query_knowledge_base, book_test_drive
# from utils.scheduler import normalize_date, normalize_time
# from datetime import datetime

# class DealershipCrew:
#     def __init__(self):
#         # Switch to 8b for higher rate limits and faster voice response
#         self.llm = LLM(
#             model=f"{Config.MODEL_NAME}",
#             api_key=Config.GROQ_TOKEN,
#             base_url="https://api.groq.com/openai/v1",
#             temperature=0
#         )

#     def _agent(self):
#         return Agent(
#             role="Receptionist",
#             goal="Book a test drive by collecting car model, date, and time.",
#             backstory=(
#                 "You are a professional dealership receptionist. "
#                 "Use the 'book_test_drive' tool ONLY when you have the model, date, and time. "
#                 "If any info is missing, ask the customer concisely using <speech> tags. "
#                 "NEVER include thoughts inside <speech>."
#             ),
#             tools=[query_knowledge_base, book_test_drive],
#             llm=self.llm,
#             verbose=True,
#             allow_delegation=False
#         )

#     def run_workflow(self, user_input: str, chat_history: str = ""):
#         """
#         Runs the workflow. 
#         Pass 'chat_history' so the agent remembers what was said in previous turns.
#         """
        
#         current_date = datetime.now().strftime("%Y-%m-%d")
#         agent = self._agent()

#         # Simplified prompt to stay under TPM limits
#         prompt_description = f"""
#         Current Date: {current_date}
        
#         Conversation History:
#         {chat_history}
        
#         New Customer Message: "{user_input}"

#         Task:
#         1. If model, date, and time are known from history or new message, CALL 'book_test_drive'.
#         2. Otherwise, ask for the missing info using <speech> tags.
#         """

#         task = Task(
#             description=prompt_description,
#             expected_output="A <speech> response or a confirmation of the booking tool call.",
#             agent=agent
#         )

#         crew = Crew(
#             agents=[agent],
#             tasks=[task],
#             process=Process.sequential,
#             verbose=True
#         )

#         result = crew.kickoff()
#         return result
    

########


# from crewai import Agent, Task, Crew, Process, LLM
# from config import Config
# from tools.search_tool import query_knowledge_base, book_test_drive
# from datetime import datetime

# class DealershipCrew:
#     def __init__(self):
#         # Using 8b-instant for high rate limits and fast voice response
#         self.llm = LLM(
#             model=f"{Config.MODEL_NAME}",
#             api_key=Config.GROQ_TOKEN,
#             base_url="https://api.groq.com/openai/v1",
#             temperature=0
#         )

#     def _agent(self):
#         return Agent(
#             role="Receptionist",
#             goal="Book a test drive by collecting the car model, date, and time.",
#             backstory=(
#                 "You are a professional dealership receptionist. "
#                 "Your goal is to get the 'model', 'date', and 'time' from the user. "
#                 "1. If info is missing, ask concisely using <speech> tags.\n"
#                 "2. If you have all three pieces of info, call the 'book_test_drive' tool immediately.\n"
#                 "3. Never put internal thoughts or 'Action' text inside <speech> tags."
#             ),
#             tools=[query_knowledge_base, book_test_drive],
#             llm=self.llm,
#             verbose=True,
#             allow_delegation=False
#         )

#     def run_workflow(self, user_input: str, chat_history: str = ""):
#         current_date = datetime.now().strftime("%Y-%m-%d")
#         agent = self._agent()

#         # The prompt provides context and history to ensure the agent remembers previous turns
#         prompt_description = f"""
#         Current Date: {current_date}
        
#         CONVERSATION HISTORY:
#         {chat_history}
        
#         NEW USER MESSAGE: "{user_input}"

#         TASK:
#         - Check if 'model', 'date', and 'time' are available in history or the new message.
#         - If YES: Call the 'book_test_drive' tool.
#         - If NO: Ask the user for the missing details using <speech> tags.
#         """

#         task = Task(
#             description=prompt_description,
#             expected_output="A <speech> response for the user or a tool call to book the drive.",
#             agent=agent
#         )

#         crew = Crew(
#             agents=[agent],
#             tasks=[task],
#             process=Process.sequential,
#             verbose=True
#         )

#         return crew.kickoff()



###################### try 33 perfectly working

# from crewai import Agent, Task, Crew, Process, LLM
# from config import Config
# from tools.search_tool import query_knowledge_base, book_test_drive
# from datetime import datetime

# class DealershipCrew:
#     def __init__(self):
#         self.llm = LLM(
#             model=f"{Config.MODEL_NAME}",
#             api_key=Config.GROQ_TOKEN,
#             base_url="https://api.groq.com/openai/v1",
#             temperature=0
#         )

#     def _agent(self):
#         return Agent(
#             role="Sales Assistant",
#             goal="Help customers discover our cars and book a test drive.",
#             backstory=(
#                 "You are a helpful dealership assistant. Your priority is to ensure the user "
#                 "chooses a model we actually have in stock before booking. "
#                 "1. ALWAYS check the 'query_knowledge_base' tool first to see available models and variants.\n"
#                 "2. If the user is vague (e.g., 'I want a car'), list the models from the database.\n"
#                 "3. Once a specific model, date, and time are confirmed, use 'book_test_drive'.\n"
#                 "4. Use <speech> tags for all verbal responses. Never show internal tool logic to the user."
#             ),
#             tools=[query_knowledge_base, book_test_drive],
#             llm=self.llm,
#             verbose=True,
#             allow_delegation=False
#         )

#     def run_workflow(self, user_input: str, chat_history: str = ""):
#         current_date = datetime.now().strftime("%Y-%m-%d")
#         agent = self._agent()

#         prompt_description = f"""
#         Current Date: {current_date}
        
#         CONVERSATION HISTORY:
#         {chat_history}
        
#         NEW USER MESSAGE: "{user_input}"

#         YOUR GUIDELINES:
#         - If the user hasn't picked a specific car, use 'query_knowledge_base' to tell them what we have (SUV vs Sedan).
#         - Validate that the requested car exists in our JSON data before booking.
#         - If 'model', 'date', and 'time' are all validated and present, call 'book_test_drive'.
#         - Otherwise, ask the user for the missing detail naturally using <speech> tags.
#         """

#         task = Task(
#             description=prompt_description,
#             expected_output="A helpful <speech> response or a confirmed booking action.",
#             agent=agent
#         )

#         crew = Crew(
#             agents=[agent],
#             tasks=[task],
#             process=Process.sequential,
#             verbose=True
#         )

#         return crew.kickoff()



from crewai import Agent, Task, Crew, Process, LLM
from config import Config
from tools.search_tool import query_knowledge_base, book_test_drive
from datetime import datetime

class DealershipCrew:
    def __init__(self):
        if not Config.GROQ_TOKEN or not Config.MODEL_NAME:
            raise ValueError("GROQ_TOKEN or MODEL_NAME not set in environment")

        self.llm = LLM(
            model=Config.MODEL_NAME,
            api_key=Config.GROQ_TOKEN,
            base_url="https://api.groq.com/openai/v1",  # GROQ endpoint
            temperature=0,
            provider="groq"  # explicitly set provider
        )

    def _agent(self):
        return Agent(
            role="Sales Assistant",
            goal="Help customers discover our cars and book a test drive.",
            backstory=(
                "You are a helpful dealership assistant. Your priority is to ensure the user "
                "chooses a model we actually have in stock before booking. "
                "1. ALWAYS check the 'query_knowledge_base' tool first to see available models and variants.\n"
                "2. If the user is vague (e.g., 'I want a car'), list the models from the database.\n"
                "3. Once a specific model, date, and time are confirmed, use 'book_test_drive'.\n"
                "4. Use <speech> tags for all verbal responses. Never show internal tool logic to the user."
            ),
            tools=[query_knowledge_base, book_test_drive],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def run_workflow(self, user_input: str, chat_history: str = ""):
        current_date = datetime.now().strftime("%Y-%m-%d")
        agent = self._agent()

        prompt_description = f"""
        Current Date: {current_date}
        
        CONVERSATION HISTORY:
        {chat_history}
        
        NEW USER MESSAGE: "{user_input}"

        YOUR GUIDELINES:
        - If the user hasn't picked a specific car, use 'query_knowledge_base' to tell them what we have (SUV vs Sedan).
        - Validate that the requested car exists in our JSON data before booking.
        - If 'model', 'date', and 'time' are all validated and present, call 'book_test_drive'.
        - Otherwise, ask the user for the missing detail naturally using <speech> tags.
        """

        task = Task(
            description=prompt_description,
            expected_output="A helpful <speech> response or a confirmed booking action.",
            agent=agent
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

        return crew.kickoff()
