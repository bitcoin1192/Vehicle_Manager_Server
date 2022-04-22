class UnknownIntent(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]

class MissingCookies(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]
