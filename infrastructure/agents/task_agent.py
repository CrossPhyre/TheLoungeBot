import json
from os import path
from core.models import Task
import shared
from infrastructure import helpers

class TaskAgent:
    def __init__(self):
        self._tasks_fp = path.join(shared.root_dir, 'shared\\data\\task.json')
        self._tasks = self.__read_tasks__()


    def __read_tasks__(self):
        if path.isfile(self._tasks_fp):
            with open(self._tasks_fp, 'r') as f:
                one_line = f.read().replace('\n', '').lstrip().rstrip()

                if one_line:
                    tasks = json.loads(one_line)
                    tasks =\
                        [Task(t['ChannelId'], t['SeqNo'], t['Title'], task_id=t['TaskId'], user_id=t['UserId'], priority=t['Priority'])
                         for t in tasks]
                else:
                    tasks = []
        else:
            tasks = []

        return tasks


    def __write_tasks__(self):
        with open(self._tasks_fp, 'w') as f:
            f.write(json.dumps([t.to_dict() for t in self._tasks]))


    def remove_task(self, channel_id, seq_no):
        t = self.get_task(channel_id, seq_no)

        if t:
            self._tasks.remove(t)
            self.__write_tasks__()

        return t


    def save_task(self, task):
        if task.channel_id and task.seq_no:
            t = self.get_task(task.channel_id, task.seq_no)

            if not t or t.task_id == task.task_id:
                if t:
                    t.user_id = task.user_id
                    t.priority = task.priority
                    t.title = task.title
                else:
                    task.task_id = max([t.task_id for t in self._tasks]) + 1 if self._tasks else 1
                    self._tasks.append(task)
                    t = task

                self.__write_tasks__()
            else:
                t = None
        else:
            t = None

        return t


    def get_task(self, channel_id, seq_no):
        task = None

        for t in self._tasks:
            if t.channel_id == channel_id and t.seq_no == seq_no:
                task = t
                break

        return task

    def get_tasks(self, filters=None):
        return helpers.filter_list(self._tasks, filters) if filters else self._tasks
