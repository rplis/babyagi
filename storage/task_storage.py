""" Storage for a single task list. """
from collections import deque
from typing import Dict, List


class SingleTaskListStorage:
    """A storage for a single task list."""

    def __init__(self):
        self.tasks = deque([])
        self.task_id_counter = 0

    def append(self, task: Dict):
        """Append a task to the task list."""
        self.tasks.append(task)

    def replace(self, tasks: List[Dict]):
        """Replace the task list with a new one."""
        self.tasks = deque(tasks)

    def popleft(self):
        """Pop the first task from the task list."""
        return self.tasks.popleft()

    def is_empty(self):
        """Return True if the task list is empty, False otherwise."""
        return False if self.tasks else True

    def next_task_id(self):
        """Return the next task id."""
        self.task_id_counter += 1
        return self.task_id_counter

    def get_task_names(self):
        """Return a list of task names."""
        return [t["task_name"] for t in self.tasks]
