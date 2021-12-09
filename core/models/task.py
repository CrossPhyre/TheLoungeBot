class Task:
    def __init__(self, channel_id, description, task_id=None, user_id=None, priority=None):
        self.task_id = task_id
        self.channel_id = channel_id
        self.description = description
        self.user_id = user_id
        self.priority = priority


    def to_dict(self):
        return\
            {
                "TaskId": self.task_id,
                "ChannelId": self.channel_id,
                "Description": self.description,
                "UserId": self.user_id,
                "Priority": self.priority
            }
