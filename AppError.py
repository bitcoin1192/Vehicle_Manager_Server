import sqlite3
class VehicleNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = "Query show 0 records"

class UserNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = "Query show 0 records"

class UserExist(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = "Username is not available"

class InputIncomplete(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = "Input is missing from request data"

class ColumnNotExist(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]

class ForeignKeyNotFound(sqlite3.IntegrityError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]

class ValueNotUnique(sqlite3.IntegrityError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]