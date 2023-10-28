"""Create tasks from stories.yaml file."""
import os

import yaml
from dotenv import load_dotenv

from classes import Epic, OpenAIAgent, Story, Task
from functions.functions import load_config, print_in_color

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

YAML_FILE_PATH = "config.yaml"
config = load_config(YAML_FILE_PATH)
LLM_MODEL = config["LLM_MODEL"].lower()
OPENAI_TEMPERATURE = float(config["OPENAI_TEMPERATURE"])
OPENAI_MAX_TOKENS = int(config["OPENAI_MAX_TOKENS"])

openai_agent = OpenAIAgent(
    model=LLM_MODEL,
    temperature=OPENAI_TEMPERATURE,
    max_tokens=OPENAI_MAX_TOKENS,
    api_key=OPENAI_API_KEY,
)

with open("stories.yaml", encoding="utf-8") as f:
    stories = yaml.safe_load(f)

print_in_color("CONFIGURATION", "BLUE")
print(f"LLM   : {LLM_MODEL}")

print_in_color("PROCESSING", "MAGENTA")

for user_story in stories["stories"]:
    story = Story(
        user_story["story_id"], user_story["name"], user_story["description"]
    )

    story = openai_agent.create_tasks(story)
    story.save_to_yaml("tasks.yaml")

    print_in_color(f"STORY: {story.name}", "red")
    for task in story.tasks:
        print(f"{task.task_id} - {task.name} - {task.description}")
