import enum


class States(enum.Enum):
    None_state = 0
    wait_for_delete = 1
    wait_for_genre = 2
    wait_arabic = 3
    wait_rus = 4
    wait_decr = 5