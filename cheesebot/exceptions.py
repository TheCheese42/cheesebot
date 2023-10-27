class CheeseBotException(Exception):
    pass


class UnprivilegedException(CheeseBotException):
    pass


class DataBaseException(CheeseBotException):
    pass


class MalformedColumn(DataBaseException):
    pass
