# Элементы таблицы имен

class Package:
    def __init__(self, name):
        self.name = name
        self.usage = False


class Const:
    def __init__(self, name, typ, value):
        self.name = name
        self.typ = typ
        self.value = value


class Var:
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ
        self.last_use = 0


class Type:
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ


class Func:
    def __init__(self, name, typ):
        self.name = name
        self.typ = typ


class Proc:
    def __init__(self, name):
        self.name = name
