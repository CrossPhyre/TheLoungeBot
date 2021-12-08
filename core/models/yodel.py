class Yodel:
    def __init__(self, yodel_id, url, stream_url, title, duration, autoqueue):
        self.yodel_id = yodel_id
        self.url = url
        self.stream_url = stream_url
        self.title = title
        self.duration = duration
        self.autoqueue = autoqueue


    def to_dict(self):
        return\
            {
                'YodelId': self.yodel_id,
                'URL': self.url,
                'StreamURL': self.stream_url,
                'Title': self.title,
                'Duration': self.duration,
                'Autoqueue': self.autoqueue
            }
