class RRSSBaseError(Exception):
    title: str

    def __init__(self, title: str):
        super().__init__(title)
        self.title = title
