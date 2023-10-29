"""Classes for the user story generator.

This module contains the classes and methods for generating user stories and
epics based on descriptions. It uses the OpenAI API for generating story names.
"""
import re
from typing import List

import openai
import yaml


class Project:
    """A Project class"""

    def __init__(self, name: str, description: str, epics=None):
        self.name = name
        self.description = description
        self.epics = epics if epics is not None else []

    def to_dict(self) -> dict:
        """Converts the project to a dictionary.

        Returns:
            A dictionary representation of the project.
        """
        return {
            "name": self.name,
            "description": self.description,
            "epics": self.epics,
        }

    def save_to_yaml(self, file_path: str):
        """Saves the project to a YAML file.

        Args:
            file_path: The path to the YAML file to save the project.
        """

        project_dict = {
            "project": {
                "name": self.name,
                "description": self.description,
                "epics": [],
            }
        }
        for epic in self.epics:
            epic_dict = epic.to_dict()
            epic_dict["stories"] = []
            for story in epic.stories:
                story_dict = story.to_dict()
                story_dict["tasks"] = []
                for task in story.tasks:
                    story_dict["tasks"].append(task.to_dict())
                epic_dict["stories"].append(story_dict)
            project_dict["project"]["epics"].append(epic_dict)
        with open(file_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(
                project_dict,
                file,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
                default_style=None,
            )


class Epic:
    """An epic.

    Attributes:
        description: A detailed description of the epic.
        stories: A list of stories that are part of this epic.
    """

    def __init__(self, epic_id: int, name: str, description: str, stories=None):
        self.epic_id = epic_id
        self.name = name
        self.description = description
        self.stories = stories if stories is not None else []

    def to_dict(self) -> dict:
        """Converts the epic to a dictionary.

        Returns:
            A dictionary representation of the epic.
        """
        return {
            "epic_id": self.epic_id,
            "name": self.name,
            "description": self.description,
        }

    def save_to_yaml(self, file_path: str):
        """Saves the epic to a YAML file.

        Args:
            file_path: The path to the YAML file to save the epic.
        """

        # build a dict with hierarchy of epic, stories and tasks
        epic_dict = {
            "epic": {
                "epic_id": self.epic_id,
                "name": self.name,
                "description": self.description,
                "stories": [],
            }
        }
        for story in self.stories:
            story_dict = story.to_dict()
            story_dict["tasks"] = []
            for task in story.tasks:
                story_dict["tasks"].append(task.to_dict())
            epic_dict["epic"]["stories"].append(story_dict)

        with open(file_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(
                epic_dict,
                file,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
                default_style=None,
            )


class Story:
    """A user story.

    Attributes:
        story_id: A unique identifier for the story.
        name: The name of the story.
        description: A detailed description of the story.
    """

    def __init__(self, story_id: int, name: str, description: str, tasks=None):
        self.story_id = story_id
        self.name = name
        self.description = description
        self.tasks = tasks if tasks is not None else []

    def to_dict(self) -> dict:
        """Converts the story to a dictionary.

        Returns:
            A dictionary representation of the story.
        """
        return {
            "story_id": self.story_id,
            "name": self.name,
            "description": self.description,
        }

    def save_to_yaml(self, file_path: str):
        """Saves the story to a YAML file.

        Args:
            file_path: The path to the YAML file to save the story.
        """
        tasks_dicts = [task.to_dict() for task in self.tasks]
        story_dict = {
            "story": {"description": self.description, "tasks": tasks_dicts}
        }

        with open(file_path, "a", encoding="utf-8") as file:
            yaml.safe_dump(
                story_dict,
                file,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False,
            )


class Task:
    """A user task."""

    def __init__(
        self, task_id: int, name: str, description: str, solution=None
    ):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.solution = solution

    def to_dict(self) -> dict:
        """Converts the task to a dictionary.

        Returns:
            A dictionary representation of the task.
        """
        return {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
        }


class OpenAIAgent:
    """OpenAI API agent for generating story names.

    Attributes:
        model: The name of the OpenAI model to use.
        temperature: The randomness of the model's output.
        max_tokens: The maximum number of tokens in the output.
        api_key: The OpenAI API key.
    """

    MAX_RETRIES = 3

    def __init__(
        self, model: str, temperature: float, max_tokens: int, api_key: str
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        openai.api_key = api_key

    def openai_call(self, prompt: str) -> str:
        """Calls the OpenAI API with a given prompt.

        Args:
            prompt: The prompt to send to the OpenAI API.

        Returns:
            The API's response.

        Raises:
            Various exceptions for API errors, timeouts, etc.
        """
        retries = 0
        while retries < self.MAX_RETRIES:
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
            retries += 1

    def create_epics(self, project: Project) -> Project:
        """Creates epics based on the project description"""
        prompt = f"""
            You are Product Owner and you work in scrum methodology using
            project, epics, stories and tasks hierarchy.
            You are to create epics based on the following project description:
            {project.description}.
            Return one epic per line in your response.
            The result must be a list in the format:

            #. First epic
            #. Second epic

            The number of each entry must be followed by a period.
            If your list is empty, write "There are no epics to add at this time.
            Unless your list is empty, do not include any headers before your numbered
            list or follow your numbered list with any other output."""

        response = self.openai_call(prompt)
        epics = response.split("\n")

        for epic_id, epic in enumerate(epics, 1):
            parts = epic.strip().split(".", 1)
            if len(parts) == 2:
                epic_id = "".join(s for s in parts[0] if s.isnumeric())
                description = re.sub(r"[^\w\s_]+", "", parts[1]).strip()

                if description.strip() and epic_id.isnumeric():
                    project.epics.append(
                        self.create_epic(int(epic_id), description)
                    )
                    print(f"{epic_id}. {description}\n")

        return project

    def create_epic(self, epic_id: int, description: str) -> Epic:
        """Creates an epic name based on its description.

        Args:
            epic_id: The ID of the epic.
            description: The description of the epic.

        Returns:
            An Epic object.
        """
        prompt = f"""You are to create an epic short name based on the
        following description: {description}. Return only one or maximum three
        words. Do not include any punctuation and apostrophies."""

        name = self.openai_call(prompt).strip()
        return Epic(int(epic_id), name, description)

    def create_stories(self, project: Project) -> Project:
        """Creates stories based on the project description"""
        for epic in project.epics:
            epic = Epic(
                epic["epic_id"],
                epic["name"],
                epic["description"],
            )

            stories = self.create_stories_from_epic(project, epic)
            epic.stories = stories
            project.epics[epic.epic_id - 1] = epic

        return project

    def create_story(self, story_id: int, description: str) -> Story:
        """Creates a story name based on its description.

        Args:
            story_id: The ID of the story.
            description: The description of the story.

        Returns:
            A Story object.
        """
        prompt = f"""You are to create a user story short name based on the
        following description: {description}. Return only one or maximum three
        words. Do not include any punctuation and apostrophies."""

        name = self.openai_call(prompt).strip()
        return Story(int(story_id), name, description)

    def create_tasks(self, project: Project) -> Project:
        """Creates tasks based on the story description"""
        for epic in project.epics:
            epic = Epic(
                epic["epic_id"],
                epic["name"],
                epic["description"],
                epic["stories"],
            )
            for story in epic.stories:
                story = Story(
                    story["story_id"],
                    story["name"],
                    story["description"],
                    story["tasks"],
                )
                story = self.create_tasks_from_story(
                    project.description, epic.description, story
                )
                epic.stories[story.story_id - 1] = story
            project.epics[epic.epic_id - 1] = epic
        return project

    def create_stories_from_epic(
        self, project: Project, epic: Epic
    ) -> List[Story]:
        """Creates stories based on the epic description"""
        prompt = f"""
            You are to create user stories. For your information main goal
            of the project is: {project.description}. But you are going to
            focus on the following epic only: {epic.description}. Please provide
            only key user stories for this particiular epic. Return one user
            story per line in your response.
            The result must be a numbered list in the format:

            #. First user story
            #. Second user story

            The number of each entry must be followed by a period.
            If your list is empty, write "There are no user stories to add at this time.
            Unless your list is empty, do not include any headers before your numbered
            list or follow your numbered list with any other output."""
        stories_lst = []
        response = self.openai_call(prompt)
        stories = response.split("\n")

        for story_id, story in enumerate(stories, 1):
            parts = story.strip().split(".", 1)
            if len(parts) == 2:
                story_id = "".join(s for s in parts[0] if s.isnumeric())
                description = re.sub(r"[^\w\s_]+", "", parts[1]).strip()

                if description.strip() and story_id.isnumeric():
                    story = self.create_story(story_id, description)
                    print(f"Story {story_id} created")
                    stories_lst.append(story)

        return stories_lst

    def create_tasks_from_story(
        self, project_description, epic_description: str, story: Story
    ):
        """Creates tasks based on the story description"""
        prompt = f"""
            You are to create tasks. The overall goal is:  {project_description}.
            Underneath is epic: {epic_description}. But you are going to
            focus on the following story only:: {story.description}.
            Please provide only key tasks for this particiular story. Return 
            one task per line in your response.
            The result must be a list in the format:

            #. First task
            #. Second task

            If your list is empty, write "There are no user tasks to add at this time.
            Unless your list is empty, do not include any headers before your numbered
            list or follow your numbered list with any other output."""

        response = self.openai_call(prompt)
        tasks = response.split("\n")

        for task_id, task in enumerate(tasks, 1):
            parts = task.strip().split(".", 1)
            if len(parts) == 2:
                task_id = "".join(s for s in parts[0] if s.isnumeric())
                description = re.sub(r"[^\w\s_]+", "", parts[1]).strip()

                if description.strip() and task_id.isnumeric():
                    task = self.create_task(task_id, description)
                    print(f"Task {task_id} created")
                    story.tasks.append(task)

        return story

    def create_task(self, task_id: int, description: str) -> Task:
        """Creates a task name based on its description.

        Args:
            task_id: The ID of the task.
            description: The description of the task.

        Returns:
            A Task object.
        """
        prompt = f"""You are to create a user task short name based on the
        following description: {description}. Return only one or maximum three
        words."""

        name = self.openai_call(prompt).strip()
        return Task(task_id, name, description)
