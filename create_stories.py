#!/usr/bin/env python3
"""
This script generates stories for an epic.
"""
import os

import yaml
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

print_in_color("CONFIGURATION", "BLUE")
print(f"MODEL   : {OPENAI_MODEL}")

print_in_color("PROJECT", "CYAN")
print(f"{PROJECT_NAME}: {PROJECT_DESCRIPTION}")

openai_agent = OpenAIAgent(
    model=OPENAI_MODEL,
    temperature=OPENAI_TEMPERATURE,
    max_tokens=OPENAI_MAX_TOKENS,
    api_key=OPENAI_API_KEY,
)

print_in_color("PROCESSING", "MAGENTA")

with open("epics.yaml", encoding="utf-8") as f:
    project = yaml.safe_load(f)

project = Project(
    name=project["project"]["name"],
    description=project["project"]["description"],
    epics=project["project"]["epics"],
)
project = openai_agent.create_stories(project)

project.save_to_yaml("stories.yaml")
