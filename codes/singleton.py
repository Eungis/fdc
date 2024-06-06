import sqlite3


# ----------------------
# Singleton Pattern
# ----------------------
class Singleton(object):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            # create the instance only one time
            # use object.__new__(Singleton) to create a new instance
            # same as: object.__new__(Singleton)
            cls.instance = super(Singleton, cls).__new__(cls)
        return cls.instance


single_1 = Singleton()
single_2 = Singleton()
print(f"if single1 == single2: {single_1 == single_2}")


# ----------------------
# Lazy Initialization
# : create the instance only when you really need it.
# : do not create the instance which is not required -> save memory.
# ----------------------
class Singleton:
    __instance = None

    def __init__(self):
        if not self.__instance:
            print("__init__ method called...")
        else:
            print(f"Instance already created: {self.get_instance()}")

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Singleton()
        return cls.__instance


single_1 = Singleton()  # Class initialized, but not created at here
print(f"Create object: {Singleton.get_instance()}")  # created at here
single_2 = Singleton()  # object is already created.


# ----------------------
# Mono State Pattern
# ----------------------


class Borg:
    __shared_state = {}

    def __init__(self):
        self.__dict__ = self.__shared_state
        pass


b = Borg()
b1 = Borg()
b.x = 4

print(f"if two objects are same?: {b == b1}")
print(f"if object states are same?: {b.__dict__ == b1.__dict__}")


# ----------------------
# Metaclass & Singleton
# : Metaclass __call__ method would be called when initializing the class instance inheriting the Metaclass object.
# : Metaclass __call__ method override __init__ and __new__ method of the target class.
# ----------------------


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        print(f"What cls means at here?: {cls}")
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=MetaSingleton):
    connection = None

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect("db.sqlite3")
            self.cursor = self.connection.cursor()
        return self.cursor


db1 = Database().connect()
db2 = Database().connect()
print(f"if db1 == db2? : {db1 == db2}")
