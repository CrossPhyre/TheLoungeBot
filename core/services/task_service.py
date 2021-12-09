from core.models import Task


class TaskService:
    def __init__(self, task_agent):
        self._task_agent = task_agent


    def add_task(self, channel_id, description, user_id, priority):
        t = self._task_agent.save_task(Task(channel_id, description, user_id=user_id, priority=priority))
        return t, None


    def assign_task(self, task_id, user_id, request_user_id):
        t, msg = self.get_task(task_id)

        if not msg:
            if user_id:
                if t.user_id is None:
                    t.user_id = user_id
                    self._task_agent.save_task(t)
                else:
                    t = None
                    msg = "Unable to claim a task that is already assigned."
            else:
                if t.user_id == request_user_id:
                    t.user_id = user_id
                    self._task_agent.save_task(t)
                else:
                    t = None
                    msg = "Unable to release a task that you are not assigned."

        return t, msg


    def get_task(self, task_id):
        t = self._task_agent.get_task(task_id)

        if t:
            msg = None
        else:
            msg = f"Unable to find a task with an sequence number of {task_id}."

        return t, msg


    def get_tasks(self, channel_id, show_all, user_id):
        tasks = self._task_agent.get_tasks()
        msg = None

        if show_all:
            tasks =\
                [t
                 for t in tasks
                 if t.channel_id == channel_id]
        else:
            if isinstance(user_id, list):
                tasks =\
                    [t
                     for t in tasks
                     if t.channel_id == channel_id
                        and t.user_id in user_id]
            else:
                tasks =\
                    [t
                     for t in tasks
                     if t.channel_id == channel_id
                        and t.user_id == user_id]

        return tasks, msg


    def remove_task(self, task_id, request_user_id):
        t, msg = self.get_task(task_id)

        if not msg:
            if t.user_id is None or t.user_id == request_user_id:
                t = self._task_agent.remove_task(task_id)
            else:
                msg = "Unable to remove a task that is assigned to another user."

        return t, msg


    def remove_tasks(self, user_id):
        tasks, msg = self.get_tasks(False, user_id)

        if not msg:
            if tasks:
                for t in tasks:
                    self._task_agent.remove_task(t.task_id)
            else:
                msg = "No tasks to remove."

        return tasks, msg


    def set_task_priority(self, task_id, priority, request_user_id):
        t, msg = self.get_task(task_id)

        if not msg:
            if t.user_id is None or t.user_id == request_user_id:
                t.priority = priority
                self._task_agent.save_task(t)
            else:
                msg = "Unable to set the priority on a task that is assigned to another user."

        return t, msg


    def set_task_title(self, task_id, description, request_user_id):
        t, msg = self.get_task(task_id)

        if not msg:
            if t.user_id is None or t.user_id == request_user_id:
                t.description = description
                self._task_agent.save_task(t)
            else:
                msg = "Unable to set the description on a task that is assigned to another user."

        return t, msg
