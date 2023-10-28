"""Create tasks from stories.yaml file."""
import os

import yaml
from dotenv import load_dotenv

from classes import Epic, OpenAIAgent
from functions.functions import load_config, print_in_color

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

YAML_FILE_PATH = "config.yaml"
config = load_config(YAML_FILE_PATH)

LLM_MODEL = config["LLM_MODEL"].lower()
OPENAI_TEMPERATURE = float(config["OPENAI_TEMPERATURE"])
OPENAI_MAX_TOKENS = int(config["OPENAI_MAX_TOKENS"])
EPIC_NAME = config["EPIC_NAME"]

openai_agent = OpenAIAgent(
    model=LLM_MODEL,
    temperature=OPENAI_TEMPERATURE,
    max_tokens=OPENAI_MAX_TOKENS,
    api_key=OPENAI_API_KEY,
)

with open(f"{EPIC_NAME}.yaml", encoding="utf-8") as f:
    objective = yaml.safe_load(f)

epic = Epic(
    name=objective["epic"]["name"],
    description=objective["epic"]["description"],
)
print_in_color("CONFIGURATION", "BLUE")
print(f"LLM   : {LLM_MODEL}")
print(f"EPIC  : {epic.name} - {epic.description}")

print_in_color("PROCESSING", "MAGENTA")

epic = openai_agent.create_tasks(epic, objective["epic"]["stories"])

epic.save_to_yaml("epic.yaml")
