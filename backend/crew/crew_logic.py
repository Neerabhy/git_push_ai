import os
import yaml
from pathlib import Path
from crewai import Agent, Task, Crew, Process

# IMPORT FIX: Import the instantiated object, NOT the class!
from backend.core.config import settings

# Force the key into the system environment so CrewAI's background processes can see it
os.environ["GROQ_API_KEY"] = settings.GROQ_API_KEY

# Get the absolute paths to our YAML files
BASE_DIR = Path(__file__).resolve().parent
AGENTS_CONFIG_PATH = BASE_DIR / 'config' / 'agents.yaml'
TASKS_CONFIG_PATH = BASE_DIR / 'config' / 'tasks.yaml'

def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

class TravelCrew:
    def __init__(self):
        # Load the YAML configurations
        self.agents_config = load_yaml(AGENTS_CONFIG_PATH)
        self.tasks_config = load_yaml(TASKS_CONFIG_PATH)

    def crew(self) -> Crew:
        # --- 1. Initialize Agents ---
        destination_expert = Agent(
            config=self.agents_config['destination_expert'],
            llm="groq/llama-3.1-8b-instant",
            verbose=False
        )
        route_coordinator = Agent(
            config=self.agents_config['route_coordinator'],
            llm="groq/llama-3.1-8b-instant",
            verbose=False
        )
        itinerary_planner = Agent(
            config=self.agents_config['itinerary_planner'],
            llm="groq/llama-3.1-8b-instant",
            verbose=False
        )

        # --- 2. Initialize Tasks ---
        destination_task = Task(
            config=self.tasks_config['destination_task'],
            agent=destination_expert
        )
        route_task = Task(
            config=self.tasks_config['route_task'],
            agent=route_coordinator
        )
        itinerary_task = Task(
            config=self.tasks_config['itinerary_task'],
            agent=itinerary_planner
        )

        # --- 3. Assemble and return the Crew ---
        return Crew(
            agents=[destination_expert, route_coordinator, itinerary_planner],
            tasks=[destination_task, route_task, itinerary_task],
            process=Process.sequential,
            verbose=False
        )