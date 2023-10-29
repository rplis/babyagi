"""
This script converts an epic, stories, and tasks from a YAML file to a CSV format 
that can be imported into Jira.
"""

import csv

import yaml


def yaml_to_jira_csv(yaml_file, csv_file):
    """
    Convert YAML data to Jira-friendly CSV format.

    Parameters:
    yaml_file (str): The path of the YAML file.
    csv_file (str): The path of the output CSV file.
    """
    # Read YAML data
    with open(yaml_file, "r") as yf:
        yaml_data = yaml.safe_load(yf)

    # Open a CSV file for writing
    with open(csv_file, "w", newline="") as cf:
        csv_writer = csv.writer(cf)

        # Write the CSV header
        csv_writer.writerow(
            ["Issue Id", "Issue Type", "Parent Id", "Summary", "Description"]
        )

        # Write epic data
        epic = yaml_data.get("epic", {})
        epic_name = epic.get("name", "")
        epic_desc = epic.get("description", "")
        csv_writer.writerow(["", "Epic", "", epic_name, epic_desc])
        epic_id = epic_name  # Assuming epic name to be unique for a Parent ID placeholder

        # Write stories and tasks data
        stories = epic.get("stories", [])
        for story in stories:
            story_id = story.get("story_id", "")
            story_name = story.get("name", "")
            story_desc = story.get("description", "")
            csv_writer.writerow(
                [story_id, "Story", epic_id, story_name, story_desc]
            )

            tasks = story.get("tasks", [])
            for task in tasks:
                task_id = task.get("task_id", "")
                task_name = task.get("name", "")
                task_desc = task.get("description", "")
                csv_writer.writerow(
                    [task_id, "Task", story_id, task_name, task_desc]
                )


if __name__ == "__main__":
    yaml_to_jira_csv("epic.yaml", "jira_output.csv")
