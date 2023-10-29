#!/usr/bin/env python3
"""
This script sets up the configuration for an artificial general
intelligence system. It imports necessary libraries and modules,
sets up environment variables, and loads extensions.
"""
import os

from dotenv import load_dotenv

from classes import OpenAIAgent, Project
from functions.functions import load_config, print_in_color

# load openai api key from .env file
load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# load configuration from config.yaml file
YAML_FILE_PATH = "config.yaml"
config = load_config(YAML_FILE_PATH)

OPENAI_MODEL = config["OPENAI_MODEL"].lower()
OPENAI_TEMPERATURE = float(config["OPENAI_TEMPERATURE"])
OPENAI_MAX_TOKENS = int(config["OPENAI_MAX_TOKENS"])

PROJECT_NAME = config["PROJECT_NAME"]
PROJECT_DESCRIPTION = config["PROJECT_DESCRIPTION"]

project = Project(PROJECT_NAME, PROJECT_DESCRIPTION)

print_in_color("CONFIGURATION", "BLUE")
print(f"LLM   : {OPENAI_MODEL}")

print_in_color("PROJECT", "CYAN")
print(f"{PROJECT_NAME}: {PROJECT_DESCRIPTION}")

openai_agent = OpenAIAgent(
    model=OPENAI_MODEL,
    temperature=OPENAI_TEMPERATURE,
    max_tokens=OPENAI_MAX_TOKENS,
    api_key=OPENAI_API_KEY,
)

print_in_color("PROCESSING", "MAGENTA")

epic = openai_agent.create_epics(project)

epic.save_to_yaml("epics.yaml")
