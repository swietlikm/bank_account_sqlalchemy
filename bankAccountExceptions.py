class BankAccountException(Exception):
    def __init__(self, message):
        self.message = message


class AccountAlreadyLoggedException(BankAccountException):
    pass


class InvalidPasswordException(BankAccountException):
    pass


class AccountAlreadyExistsException(BankAccountException):
    pass


class AccountNotLoggedException(BankAccountException):
    pass


class AccountUsernameNotFound(BankAccountException):
    pass
