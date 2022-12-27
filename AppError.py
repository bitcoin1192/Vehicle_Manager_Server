from ast import arg
import sqlite3
class VehicleNotFound(sqlite3.IntegrityError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]

class UserNotFound(sqlite3.IntegrityError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]

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

class ZeroRowAffected(sqlite3.OperationalError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]

class PermissionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.error = args[0]