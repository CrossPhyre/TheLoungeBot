class Goal:
    def __init__(self, channel_id, user_id, seq_no, title, task_id=None, priority=None):
        self.task_id = task_id
        self.channel_id = channel_id
        self.seq_no = seq_no
        self.title = title
        self.user_id = user_id
        self.priority = priority


    def to_dict(self):
        return\
            {
                "TaskId": self.task_id,
                "ChannelId": self.channel_id,
                "SeqNo": self.seq_no,
                "Title": self.title,
                "UserId": self.user_id,
                "Priority": self.priority
            }
