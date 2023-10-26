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

import importlib
import os
import re
import time
from typing import Dict, List

import chromadb
import openai
import tiktoken
from chromadb.config import Settings
from colorama import Fore, Style
from dotenv import load_dotenv

from storage import SingleTaskListStorage
from storage.chromadb import DefaultResultsStorage

# Load default environment variables (.env)
load_dotenv()

# default opt out of chromadb telemetry.
client = chromadb.Client(Settings(anonymized_telemetry=False))

# Model: GPT, LLAMA, HUMAN, etc.
LLM_MODEL = os.getenv("LLM_MODEL", os.getenv("OPENAI_API_MODEL")).lower()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Table config
RESULTS_STORE_NAME = os.getenv(
    "RESULTS_STORE_NAME", os.getenv("TABLE_NAME", "")
)

# Run configuration
INSTANCE_NAME = os.getenv("INSTANCE_NAME", "BabyAGI")
COOPERATIVE_MODE = os.getenv("COOPERATIVE_MODE", "none").lower()
JOIN_EXISTING_OBJECTIVE = False

# Goal configuration
OBJECTIVE = os.getenv("OBJECTIVE", "")
INITIAL_TASK = os.getenv("INITIAL_TASK", os.getenv("FIRST_TASK", ""))

# Model configuration
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))


# Extensions support begin
def can_import(module_name):
    """Checks if a module can be imported."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


DOTENV_EXTENSIONS = os.getenv("DOTENV_EXTENSIONS", "").split(" ")

# Command line arguments extension
# Can override any of the above environment variables
ENABLE_COMMAND_LINE_ARGS = (
    os.getenv("ENABLE_COMMAND_LINE_ARGS", "false").lower() == "true"
)
if ENABLE_COMMAND_LINE_ARGS:
    if can_import("extensions.argparseext"):
        from extensions.argparseext import parse_arguments

        (
            OBJECTIVE,
            INITIAL_TASK,
            LLM_MODEL,
            DOTENV_EXTENSIONS,
            INSTANCE_NAME,
            COOPERATIVE_MODE,
            JOIN_EXISTING_OBJECTIVE,
        ) = parse_arguments()

# Human mode extension
# Gives human input to babyagi
if LLM_MODEL.startswith("human"):
    if can_import("extensions.human_mode"):
        from extensions.human_mode import user_input_await

# Load additional environment variables for enabled extensions
# Note: This might override the following command line arguments as well:
# OBJECTIVE, INITIAL_TASK, LLM_MODEL, INSTANCE_NAME, COOPERATIVE_MODE,
# JOIN_EXISTING_OBJECTIVE
if DOTENV_EXTENSIONS:
    if can_import("extensions.dotenvext"):
        from extensions.dotenvext import load_dotenv_extensions

        load_dotenv_extensions(DOTENV_EXTENSIONS)

# Note: There's still work to be done here to enable people to get
# defaults from dotenv extensions, but also provide command line
# arguments to override them

print(
    f"{Fore.BLUE}{Style.BRIGHT}"
    + "\n*****CONFIGURATION*****\n"
    + f"{Style.RESET_ALL}"
)
print(f"Name  : {INSTANCE_NAME}")
print(
    f"Mode : {'alone' if COOPERATIVE_MODE in ['n', 'none'] else 'local' if COOPERATIVE_MODE in ['l', 'local'] else 'distributed' if COOPERATIVE_MODE in ['d', 'distributed'] else 'undefined'}"
)
print(f"LLM   : {LLM_MODEL}")

# Check if we know what we are doing
if LLM_MODEL.startswith("gpt-4"):
    print(
        f"{Fore.RED}{Style.BRIGHT}"
        + "\n*****USING GPT-4. POTENTIALLY EXPENSIVE. MONITOR YOUR COSTS*****"
        + f"{Style.RESET_ALL}"
    )

if LLM_MODEL.startswith("human"):
    print(
        f"{Fore.LIGHTWHITE_EX}"
        + "\n*****USING HUMAN INPUT*****"
        + f"{Style.RESET_ALL}"
    )

print(
    f"{Fore.CYAN}{Style.BRIGHT}"
    + "\n*****OBJECTIVE*****\n"
    + f"{Style.RESET_ALL}"
)
print(f"{OBJECTIVE}")

if not JOIN_EXISTING_OBJECTIVE:
    print(
        f"{Fore.MAGENTA}{Style.BRIGHT}"
        + "\n*****INITIAL TASK*****\n"
        + f"{Style.RESET_ALL}"
        + f" {INITIAL_TASK}"
    )


results_storage = DefaultResultsStorage()  # chromedb

tasks_storage = SingleTaskListStorage()


def limit_tokens_from_string(string: str, model: str, limit: int) -> str:
    """Limits the string to a number of tokens (estimated)."""

    encoding = tiktoken.encoding_for_model(model)

    encoded = encoding.encode(string)

    return encoding.decode(encoded[:limit])


def openai_call(
    prompt: str,
    model: str = LLM_MODEL,
    temperature: float = OPENAI_TEMPERATURE,
    max_tokens: int = 100,
):
    """OpenAI API call."""
    while True:
        try:
            if model.lower().startswith("human"):
                return user_input_await(prompt)
            elif not model.lower().startswith("gpt-"):
                response = openai.Completion.create(
                    engine=model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                return response.choices[0].text.strip()
            else:
                # Use 4000 instead of the real limit (4097) to give a bit
                # of wiggle room for the encoding of roles.
                # Note: different limits for different models.

                trimmed_prompt = limit_tokens_from_string(
                    prompt, model, 4000 - max_tokens
                )

                # Use chat completion API
                messages = [{"role": "system", "content": trimmed_prompt}]
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1,
                    stop=None,
                )
                return response.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            print(
                "   *** The OpenAI API rate limit has been exceeded."
                " Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.Timeout:
            print(
                "   *** OpenAI API timeout occurred."
                " Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.APIError:
            print(
                "   *** OpenAI API error occurred."
                " Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.APIConnectionError:
            print(
                "   *** OpenAI API connection error occurred."
                " Check your network settings, proxy configuration, SSL "
                " certificates, or firewall rules. Waiting 10 seconds "
                " and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.InvalidRequestError:
            print(
                "   *** OpenAI API invalid request. Check the documentation "
                " for the specific API method you are calling and make sure"
                " you are sending valid and complete parameters. "
                " Waiting 10 seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        except openai.error.ServiceUnavailableError:
            print(
                "   *** OpenAI API service unavailable. Waiting 10 "
                " seconds and trying again. ***"
            )
            time.sleep(10)  # Wait 10 seconds and try again
        else:
            break


def task_creation_agent(
    objective: str, result: Dict, task_description: str, task_list: List[str]
):
    """Creates new tasks based on the result of a previous task."""
    prompt = f"""
You are to use the result from an execution agent to create new tasks with
the following objective: {objective}. The last completed task has the
result: \n{result["data"]}
This result was based on this task description: {task_description}.\n"""

    if task_list:
        prompt += f"These are incomplete tasks: {', '.join(task_list)}\n"
    prompt += """Based on the result, return a list of tasks to be
    completed in order to meet the objective. """
    if task_list:
        prompt += "These new tasks must not overlap with incomplete tasks. "

    prompt += """
Return one task per line in your response.
The result must be a numbered list in the format:

#. First task
#. Second task

The number of each entry must be followed by a period.
If your list is empty, write "There are no tasks to add at this time.
Unless your list is empty, do not include any headers before your numbered
list or follow your numbered list with any other output."""

    # print(
    #     f"\n{Fore.LIGHTGREEN_EX}{Style.BRIGHT}*****TASK CREATION AGENT PROMPT****{Style.RESET_ALL}\n{prompt}\n"
    # )
    response = openai_call(prompt, max_tokens=2000)
    # print(
    #     f"\n{Fore.LIGHTGREEN_EX}{Style.BRIGHT}****TASK CREATION AGENT RESPONSE****{Style.RESET_ALL}\n{response}\n"
    # )
    new_tasks = response.split("\n")
    new_tasks_list = []
    for task_string in new_tasks:
        task_parts = task_string.strip().split(".", 1)
        if len(task_parts) == 2:
            task_id = "".join(s for s in task_parts[0] if s.isnumeric())
            task_name = re.sub(r"[^\w\s_]+", "", task_parts[1]).strip()
            if task_name.strip() and task_id.isnumeric():
                new_tasks_list.append(task_name)

    out = [{"task_name": task_name} for task_name in new_tasks_list]
    return out


def prioritization_agent():
    """Prioritizes tasks based on the objective."""
    task_names = tasks_storage.get_task_names()
    bullet_string = "\n"

    prompt = f"""
You are tasked with prioritizing the following 
tasks: {bullet_string + bullet_string.join(task_names)}
Consider the ultimate objective of your team: {OBJECTIVE}.
Tasks should be sorted from highest to lowest priority, where higher-priority
tasks are those that act as pre-requisites or are more essential for
meeting the objective. Do not remove any tasks. Return the ranked tasks
as a numbered list in the format:

#. First task
#. Second task

The entries must be consecutively numbered, starting with 
1. The number of each entry must be followed by a period.
Do not include any headers before your ranked list or
follow your list with any other output."""

    # print(f"\n****TASK PRIORITIZATION AGENT PROMPT****\n{prompt}\n")
    response = openai_call(prompt, max_tokens=2000)
    print(
        f"\n{Fore.LIGHTGREEN_EX}{Style.BRIGHT}****TASK PRIORITIZATION AGENT RESPONSE****{Style.RESET_ALL}\n{response}\n"
    )
    if not response:
        print(
            """Received empty response from priotritization agent.
            Keeping task list unchanged."""
        )
        return
    new_tasks = response.split("\n") if "\n" in response else [response]
    new_tasks_list = []
    for task_string in new_tasks:
        task_parts = task_string.strip().split(".", 1)
        if len(task_parts) == 2:
            task_id = "".join(s for s in task_parts[0] if s.isnumeric())
            task_name = re.sub(r"[^\w\s_]+", "", task_parts[1]).strip()
            if task_name.strip():
                new_tasks_list.append(
                    {"task_id": task_id, "task_name": task_name}
                )

    return new_tasks_list


def execution_agent(objective: str, task: str) -> str:
    """
    Executes a task based on the given objective and previous context.

    Args:
        objective (str): The objective or goal for the AI to perform the task.
        task (str): The task to be executed by the AI.

    Returns:
        str: The response generated by the AI for the given task.

    """

    context = context_agent(query=objective, top_results_num=5)
    prompt = (
        f"Perform one task based on the following objective: {objective}.\n"
    )
    if context:
        prompt += (
            "Take into account these previously completed tasks:"
            + "\n".join(context)
        )
    prompt += f"\nYour task: {task}\nResponse:"
    return openai_call(prompt, max_tokens=2000)


def context_agent(query: str, top_results_num: int):
    """
    Retrieves context for a given query from an index of tasks.

    Args:
        query (str): The query or objective for retrieving context.
        top_results_num (int): The number of top results to retrieve.

    Returns:
        list: A list of tasks as context for the given query, sorted
        by relevance.

    """
    results = results_storage.query(
        query=query, top_results_num=top_results_num
    )
    return results


# Add the initial task if starting new objective
if not JOIN_EXISTING_OBJECTIVE:
    initial_task = {
        "task_id": tasks_storage.next_task_id(),
        "task_name": INITIAL_TASK,
    }
    tasks_storage.append(initial_task)


def main():
    """Main function for BabyAGI."""
    loop = 0
    while loop < 1:
        loop += 1
        # As long as there are tasks in the storage...
        if not tasks_storage.is_empty():
            # Print the task list
            print(
                f"{Fore.LIGHTMAGENTA_EX}{Style.DIM}"
                + "\n*****TASK LIST*****\n"
                + f"{Style.RESET_ALL}"
            )
            for t in tasks_storage.get_task_names():
                print(" • " + str(t))

            # Step 1: Pull the first incomplete task
            task = tasks_storage.popleft()
            print(
                f"{Fore.CYAN}{Style.NORMAL}"
                + "\n*****NEXT TASK*****\n"
                + f"{Style.RESET_ALL}"
            )
            print(str(task["task_name"]))

            # Send to execution function to complete task based on the context
            result = execution_agent(OBJECTIVE, str(task["task_name"]))
            print(
                f"{Fore.GREEN}{Style.BRIGHT}"
                + "\n*****TASK RESULT*****\n"
                + f"{Style.RESET_ALL}"
            )
            print(result)

            # Step 2: Enrich result and store in the results storage
            # This is where you should enrich the result if needed
            enriched_result = {"data": result}
            # extract the actual result from the dictionary
            # since we don't do enrichment currently
            # vector = enriched_result["data"]

            result_id = f"result_{task['task_id']}"

            results_storage.add(task, result, result_id)

            # Step 3: Create new tasks and re-prioritize task list
            # only the main instance in cooperative mode does that
            new_tasks = task_creation_agent(
                OBJECTIVE,
                enriched_result,
                task["task_name"],
                tasks_storage.get_task_names(),
            )

            # print(
            #     f"{Fore.BLUE}Adding new tasks to task_storage{Style.RESET_ALL}"
            # )
            for new_task in new_tasks:
                new_task.update({"task_id": tasks_storage.next_task_id()})
                # print(str(new_task))
                tasks_storage.append(new_task)

            if not JOIN_EXISTING_OBJECTIVE:
                prioritized_tasks = prioritization_agent()
                if prioritized_tasks:
                    tasks_storage.replace(prioritized_tasks)

            # Sleep a bit before checking the task list again
            time.sleep(5)
        else:
            print("Done.")
            loop = False


if __name__ == "__main__":
    main()
