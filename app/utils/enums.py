from enum import (
    Enum, 
    StrEnum
)


class Roles(Enum):
    ADMIN = 99
    PARENT = 1


class GenderTypes(Enum):
    MALE = 1
    FEMALE = 2    


class Days(StrEnum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    Sunday = "Sunday"

class OrderByTypes(StrEnum):
    """
        Enumeration of sorting types.
    """
    ASC = "asc"
    DESC = "desc"   

class EMAIL_TASK_STATUS(StrEnum):
    SENDING = "SENDING"
    SENT = "SENT"
    FAILED = "FAILED"     