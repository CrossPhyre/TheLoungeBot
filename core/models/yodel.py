class Yodel:
    def __init__(self, yodel_id, url, title, duration, autoqueue):
        self.yodel_id = yodel_id
        self.url = url
        self.title = title
        self.duration = duration
        self.autoqueue = autoqueue


    def to_dict(self):
        return\
            {
                'YodelId': self.yodel_id,
                'URL': self.url,
                'Title': self.title,
                'Duration': self.duration,
                'Autoqueue': self.autoqueue
            }
