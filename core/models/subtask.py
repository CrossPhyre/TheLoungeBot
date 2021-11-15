class Subtask:
    def __init__(self, task_id, seq_no, title, subtask_id=None, priority=None):
        self.subtask_id = subtask_id
        self.task_id = task_id
        self.seq_no = seq_no
        self.title = title
        self.priority = priority


    def to_dict(self):
        return\
            {
                'SubtaskId': self.subtask_id,
                'TaskId': self.task_id,
                'SeqNo': self.seq_no,
                'Title': self.title,
                'Priority': self.priority
            }
