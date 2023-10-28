"""
This script converts an epic, stories, and tasks from a YAML file to a CSV file.
"""

import csv

import yaml


def yaml_to_csv(yaml_file, csv_file):
    """
    Convert YAML data to CSV format.

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
        csv_writer.writerow(["Type", "ID", "Name", "Description"])

        # Write epic data
        epic = yaml_data.get("epic", {})
        csv_writer.writerow(
            ["Epic", "", epic.get("name", ""), epic.get("description", "")]
        )

        # Write stories and tasks data
        stories = epic.get("stories", [])
        for story in stories:
            story_id = story.get("story_id", "")
            csv_writer.writerow(
                [
                    "Story",
                    story_id,
                    story.get("name", ""),
                    story.get("description", ""),
                ]
            )

            tasks = story.get("tasks", [])
            for task in tasks:
                task_id = task.get("task_id", "")
                csv_writer.writerow(
                    [
                        "Task",
                        task_id,
                        task.get("name", ""),
                        task.get("description", ""),
                    ]
                )


if __name__ == "__main__":
    yaml_to_csv("epic.yaml", "output.csv")
