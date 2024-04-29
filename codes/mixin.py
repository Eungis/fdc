class BaseTokenizer:
    def __init__(self, sent):
        self.sent = sent

    def __iter__(self):
        print("Start __iter__ function")
        sent = self.sent.split("-")
        yield from sent


class UpperIterableMixin:
    # Mixin does not require to call __init__

    def __iter__(self):
        return map(str.upper, super().__iter__())


class Tokenizer(BaseTokenizer, UpperIterableMixin):
    pass


# database example


class LoggableMixin:
    def __init__(self):
        print("Initialize LoggableMixin")  # will not be called
        self.title = ""

    def log(self):
        print("Log message from: ", self.title)


class ConnectionMixin:
    def __init__(self):
        print("Initialize ConnectionMixin")  # will not be called
        self.server = ""

    def connect(self):
        print("Connect to server: ", self.server)


class SQLDatabase(ConnectionMixin, LoggableMixin):
    def __init__(self):
        print("Initialize SQLDatabase")
        self.title = "SQL Database"
        self.server = "0.0.0.0:1"


if __name__ == "__main__":
    tokenizer = Tokenizer(sent="year-day-month")
    # for loop wraps the iterater using __iter__
    for token in tokenizer:
        print(token)

    # same for list()
    tokenizer = Tokenizer(sent="year-day-month")
    print(list(tokenizer))

    # database example
    def framework(item):
        if isinstance(item, ConnectionMixin):
            item.connect()
        if isinstance(item, LoggableMixin):
            item.log()

    db = SQLDatabase()
    framework(db)
