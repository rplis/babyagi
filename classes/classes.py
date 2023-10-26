"""Classes for the user story generator."""
import re
import time

import openai
import yaml


class Story:
    """A user story."""

    def __init__(self, story_id: int, name: str, description: str):
        self.story_id = story_id
        self.name = name
        self.description = description

    def to_dict(self):
        """Converts story to dictionary."""
        return {
            "story_id": self.story_id,
            "name": self.name,
            "description": self.description,
        }


class Epic:
    """An epic."""

    def __init__(self, description: str):
        self.description = description
        self.stories = []

    def save_to_yaml_file(self, file_path: str):
        """Saves epic to yaml file."""
        stories_dicts = [story.to_dict() for story in self.stories]

        epic_dict = {"description": self.description, "stories": stories_dicts}

        with open(file_path, "w", encoding="utf-8") as file:
            yaml.dump(epic_dict, file)


class OpenAIAgent:
    """OpenAI API agent."""

    def __init__(
        self, model: str, temperature: float, max_tokens: int, api_key: str
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        openai.api_key = self.api_key

    def openai_call(self, prompt: str):
        """OpenAI API call."""
        while True:
            try:
                messages = [{"role": "system", "content": prompt}]
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    n=1,
                    stop=None,
                )
                return response.choices[0].message.content.strip()
            except openai.error.Timeout as e:
                print(f"OpenAI API request timed out: {e}")
            except openai.error.APIError as e:
                print(f"OpenAI API returned an API Error: {e}")
            except openai.error.APIConnectionError as e:
                print(f"OpenAI API request failed to connect: {e}")
            except openai.error.InvalidRequestError as e:
                print(f"OpenAI API request was invalid: {e}")
            except openai.error.AuthenticationError as e:
                print(f"OpenAI API request was not authorized: {e}")
            except openai.error.PermissionError as e:
                print(f"OpenAI API request was not permitted: {e}")
            except openai.error.RateLimitError as e:
                print(f"OpenAI API request exceeded rate limit: {e}")
            except openai.error.OpenAIError as e:
                print(f"OpenAI API request failed: {e}")
            except Exception as e:
                print(f"Unknown error: {e}")

    def create_stories(self, epic: Epic):
        """Creates stories based on the epic description"""
        prompt = f"""
            You are to create user stories based on the following epic: {epic.description}.
            Return one user story per line in your response.
            The result must be a numbered list in the format:

            #. First user story
            #. Second user story

            The number of each entry must be followed by a period.
            If your list is empty, write "There are no user stories to add at this time.
            Unless your list is empty, do not include any headers before your numbered
            list or follow your numbered list with any other output."""

        response = self.openai_call(prompt)
        new_user_stories = response.split("\n")
        new_user_stories_list = []
        for story_id, user_story in enumerate(new_user_stories, 1):
            user_story_parts = user_story.strip().split(".", 1)
            if len(user_story_parts) == 2:
                user_story_id = "".join(
                    s for s in user_story_parts[0] if s.isnumeric()
                )
                description = re.sub(
                    r"[^\w\s_]+", "", user_story_parts[1]
                ).strip()
                if description.strip() and user_story_id.isnumeric():
                    epic.stories.append(
                        self.create_story(int(user_story_id), description)
                    )
                    print(f"Story {user_story_id} created.")
                    time.sleep(1)
        return epic

    def create_story(self, story_id: int, description: str) -> Story:
        """Creates story name based on the story description"""
        prompt = f"""
            You are to create user story short name based on the following description: {description}.
            Return only one or maximum two words."""
        response = self.openai_call(prompt)
        name = response.strip()
        return Story(story_id, name, description)
