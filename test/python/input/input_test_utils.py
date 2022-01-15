from enum import Enum, auto

class KeyType(Enum):
    TAB = auto()
    SHIFT = auto()
    ESC = auto()
    F3 = auto()

class InputEvent:
    def __init__(self, inst, key, ts):
        self.inst = inst
        self.keytype = key
        self.time = ts

    def __str__(self):
        return '{} {}'.format(self.inst, self.keytype.name)