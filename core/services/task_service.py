from core.models import Task


class TaskService:
    def __init__(self, task_agent):
        self._task_agent = task_agent


    def __contains_title__(self, tasks, title):
        duplicate = False

        for t in tasks:
            if t.title == title:
                duplicate = True
                break

        if duplicate:
            msg = "A task already exists with the title \'{}\'.".format(title)
        else:
            msg = None

        return duplicate, msg


    def add_task(self, channel_id, title, user_id, priority, request_user_id):
        tasks, msg = self.get_tasks(channel_id, True, None, request_user_id)

        if not msg:
            duplicate, msg = self.__contains_title__(tasks, title)

            if not duplicate:
                next_seq_no = max([t.seq_no for t in tasks]) + 1 if tasks else 1
                t = self._task_agent.save_task(Task(channel_id, next_seq_no, title, user_id=user_id, priority=priority))
            else:
                t = None
        else:
            t = None

        return t, msg


    def assign_task(self, channel_id, seq_no, user_id, request_user_id):
        t, msg = self.get_task(channel_id, seq_no, request_user_id)

        if not msg:
            if user_id:
                if t.user_id is None:
                    t.user_id = user_id
                    self._task_agent.save_task(t)
                else:
                    t = None
                    msg = 'Unable to claim a task that is already assigned.'
            else:
                if t.user_id == request_user_id:
                    t.user_id = user_id
                    self._task_agent.save_task(t)
                else:
                    t = None
                    msg = 'Unable to release a task that you are not assigned.'

        return t, msg


    def condense(self, channel_id, request_user_id):
        tasks, msg = self.get_tasks(channel_id, True, None, request_user_id)

        if not msg:
            if tasks:
                tasks = sorted(tasks, key=lambda t: t.seq_no)
                for i, t in enumerate(tasks):
                    t.seq_no = i + 1
                    self._task_agent.save_task(t)
            else:
                msg = 'There were no tasks to condense.'

        return tasks, msg


    def get_task(self, channel_id, seq_no, request_user_id):
        t = self._task_agent.get_task(channel_id, seq_no)

        if t:
            msg = None
        else:
            msg = 'Unable to find a task with an sequence number of {}.'.format(seq_no)

        return t, msg


    def get_tasks(self, channel_id, show_all, user_id, request_user_id):
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


    def remove_task(self, channel_id, seq_no, request_user_id):
        t, msg = self.get_task(channel_id, seq_no, request_user_id)

        if not msg:
            if t.user_id is None or t.user_id == request_user_id:
                t = self._task_agent.remove_task(channel_id, seq_no)
            else:
                msg = 'Unable to remove a task that is assigned to another user.'

        return t, msg


    def remove_tasks(self, channel_id, user_id, request_user_id):
        tasks, msg = self.get_tasks(channel_id, False, user_id, request_user_id)

        if not msg:
            if tasks:
                for t in tasks:
                    self._task_agent.remove_task(channel_id, t.seq_no)
            else:
                msg = 'No tasks to remove.'

        return tasks, msg


    def set_task_priority(self, channel_id, seq_no, priority, request_user_id):
        t, msg = self.get_task(channel_id, seq_no, request_user_id)

        if not msg:
            if t.user_id is None or t.user_id == request_user_id:
                t.priority = priority
                self._task_agent.save_task(t)
            else:
                msg = 'Unable to set the priority on a task that is assigned to another user.'

        return t, msg


    def set_task_title(self, channel_id, seq_no, title, request_user_id):
        t, msg = self.get_task(channel_id, seq_no, request_user_id)

        if not msg:
            if t.user_id is None or t.user_id == request_user_id:
                tasks, msg = self.get_tasks(channel_id, True, None, request_user_id)

                if not msg:
                    duplicate, msg = self.__contains_title__(tasks, title)

                    if not duplicate:
                        t.title = title
                        self._task_agent.save_task(t)
            else:
                msg = 'Unable to set the title on a task that is assigned to another user.'

        return t, msg
