"""Create tasks from stories.yaml file."""
import os

import yaml
from dotenv import load_dotenv

from classes import OpenAIAgent, Project
from functions.functions import load_config, print_in_color

# Load OPENAI_API_KEY from .env file
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Load config.yaml file
YAML_FILE_PATH = "config.yaml"
config = load_config(YAML_FILE_PATH)

OPENAI_MODEL = config["OPENAI_MODEL"].lower()
OPENAI_TEMPERATURE = float(config["OPENAI_TEMPERATURE"])
OPENAI_MAX_TOKENS = int(config["OPENAI_MAX_TOKENS"])

PROJECT_NAME = config["PROJECT_NAME"]

openai_agent = OpenAIAgent(
    model=OPENAI_MODEL,
    temperature=OPENAI_TEMPERATURE,
    max_tokens=OPENAI_MAX_TOKENS,
    api_key=OPENAI_API_KEY,
)

with open("stories.yaml", encoding="utf-8") as f:
    project = yaml.safe_load(f)

project = Project(
    name=project["project"]["name"],
    description=project["project"]["description"],
    epics=project["project"]["epics"],
)

print_in_color("CONFIGURATION", "BLUE")
print(f"OPENAI_MODEL   : {OPENAI_MODEL}")
print(f"PROJECT  : {project.name} - {project.description}")

print_in_color("PROCESSING", "MAGENTA")

project = openai_agent.create_tasks(project)

project.save_to_yaml("tasks.yaml")
