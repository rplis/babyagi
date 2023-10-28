#!/usr/bin/env python3
"""
This script sets up the configuration for BabyAGI, an artificial general
intelligence system. 
It imports necessary libraries and modules, sets up environment variables,
and loads extensions.
It also checks if the required environment variables are present and
initializes the Llama model if required.
Finally, it prints the configuration details for BabyAGI.
"""
import os

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
EPIC_DESCRIPTION = config["EPIC_DESCRIPTION"]
epic = Epic(EPIC_NAME, EPIC_DESCRIPTION)

print_in_color("CONFIGURATION", "BLUE")

print(f"LLM   : {LLM_MODEL}")

print_in_color("EPIC", "CYAN")

print(f"{EPIC_NAME}: {EPIC_DESCRIPTION}")

openai_agent = OpenAIAgent(
    model=LLM_MODEL,
    temperature=OPENAI_TEMPERATURE,
    max_tokens=OPENAI_MAX_TOKENS,
    api_key=OPENAI_API_KEY,
)

print_in_color("PROCESSING", "MAGENTA")

epic = openai_agent.create_stories(epic)

epic.save_to_yaml(f"{EPIC_NAME}.yaml")
