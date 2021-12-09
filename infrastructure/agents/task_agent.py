import json
from os import path
from core.models import Task
import shared
from infrastructure import helpers

class TaskAgent:
    def __init__(self):
        self._tasks_fp = path.join(shared.root_dir, "shared\\data\\task.json")
        self._tasks = self.__read_tasks__()


    def __read_tasks__(self):
        if path.isfile(self._tasks_fp):
            with open(self._tasks_fp, "r") as f:
                json_str = f.read().replace("\n", "").lstrip().rstrip()

                if json_str:
                    tasks = json.loads(json_str)
                    tasks =\
                        {t["TaskId"]: Task(t["ChannelId"], t["Description"], task_id=t["TaskId"], user_id=t["UserId"], priority=t["Priority"])
                         for t in tasks}
                else:
                    tasks = {}
        else:
            tasks = {}

        return tasks


    def __write_tasks__(self):
        with open(self._tasks_fp, "w") as f:
            f.write(json.dumps([t.to_dict() for t in self._tasks.values()]))


    def remove_task(self, task_id):
        t = self._tasks.pop(task_id, None)

        if t:
            self.__write_tasks__()

        return t


    def save_task(self, task):
        t = None
        needs_saved = False

        if not task.task_id:
            task.task_id = max(self._tasks.keys()) + 1 if self._tasks else 1
            self._tasks[task.task_id] = task
            t = task
            needs_saved = True
        else:
            t = self.get_task(task.task_id)

            if t:
                t.user_id = task.user_id
                t.priority = task.priority
                t.description = task.description
                needs_saved = True

        if needs_saved:
            self.__write_tasks__()

        return t


    def get_task(self, task_id):
        return self._tasks.get(task_id, None)

    def get_tasks(self, filters=None):
        task_list = list(t for t in self._tasks.values())
        return helpers.filter_list(task_list, filters) if filters else task_list
