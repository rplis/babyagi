# Task storage supporting only a single instance of BabyAGI
from collections import deque
from typing import Dict, List


class SingleTaskListStorage:
    """A simple task storage that supports only a single instance of BabyAGI.
    Parameters:
    ----------
    tasks: deque
        A deque of tasks
    task_id_counter: int
        A counter for task ids
    Methods:
    -------
    append(task: Dict)
        Append a task to the task list
    replace(tasks: List[Dict])
        Replace the current task list with a new one
    popleft()
        Pop the first task from the task list
    is_empty()
        Check if the task list is empty
    next_task_id()
        Return the next task id
    get_task_names()
        Return a list of task names
    """

    def __init__(self):
        self.tasks = deque([])
        self.task_id_counter = 0

    def append(self, task: Dict):
        self.tasks.append(task)

    def replace(self, tasks: List[Dict]):
        self.tasks = deque(tasks)

    def popleft(self):
        return self.tasks.popleft()

    def is_empty(self):
        return False if self.tasks else True

    def next_task_id(self):
        self.task_id_counter += 1
        return self.task_id_counter

    def get_task_names(self):
        return [t["task_name"] for t in self.tasks]
