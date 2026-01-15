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
            base_url="https://api.groq.com/openai/v1",  
            temperature=0,
            provider="groq"  
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
