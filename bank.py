import getpass
import logging
import os
import random
import string
from datetime import datetime
import bankAccountExceptions
from models import Users, Owners, BankAccounts, Transactions, TransactionTypes
from setup import create_engine

from sqlalchemy.orm import Session

clear = lambda: os.system("cls")
engine = create_engine()
session = Session(engine)

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    filename="bank.log",
    format="%(asctime)s:%(levelname)s:%(message)s ",
)


def create_account():
    try:
        username = get_valid_input("Username: ", username_is_valid)
        password = get_valid_input("Password: ", password_is_valid)
        first_name = get_valid_input("First name: ")
        last_name = get_valid_input("Last name: ")
        email = get_valid_input("Email: ", email_is_valid)
        ssn = get_valid_input("SSN: ", ssn_is_valid)
        phone_number = get_valid_input("Phone number: ", phone_is_valid)
    except ValueError as e:
        print(str(e))
        return

    with session:
        # Add new owner to the database
        owner = Owners(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            ssn=ssn,
        )

        # Add new User to the database (1 to 1 with Owner)
        user = Users(username=username, owner=owner)
        user.set_password(password=password)

        # Add new BankAccount to the database (1 to 1 with User)
        bank_account = BankAccounts(
            balance=0,
            account_number=generate_account_number(),
            status="active",
            created_at=datetime.now(),
            user=user,
        )

        session.add_all([owner, user, bank_account])
        session.commit()
    logging.info(f"New account created, username: {username}")
    print("Account successfully created")


def get_valid_input(prompt, is_valid=None):
    while True:
        value = input(f">>> {prompt}")
        if is_valid:
            try:
                is_valid(value)
            except ValueError as e:
                print(str(e))
                continue
        return value


def username_is_valid(username):
    with Session(engine) as session:
        query = session.query(Users.username).filter(Users.username == username).first()
        if query:
            raise ValueError("This username already exists")


def account_number_is_valid(account_number):
    with session:
        query = (
            session.query(BankAccounts.account_number)
            .filter(BankAccounts.account_number == account_number)
            .first()
        )
        if query:
            return False
    return True


def email_is_valid(email):
    with Session(engine) as session:
        query = session.query(Owners.email).filter(Owners.email == email).first()
        if query:
            raise ValueError("This email already exists in database")


def ssn_is_valid(ssn):
    with Session(engine) as session:
        query = session.query(Owners.ssn).filter(Owners.ssn == ssn).first()
        if query:
            raise ValueError("This SSN already exists in database")


def phone_is_valid(phone_number):
    with Session(engine) as session:
        query = (
            session.query(Owners.phone_number)
            .filter(Owners.phone_number == phone_number)
            .first()
        )
        if query:
            raise ValueError("This phone number already exists in database")


def password_is_valid(password):
    # TODO password validation logic
    return True


def generate_account_number():
    account_number = "7810106666" + "".join(random.choices(string.digits, k=16))
    while not account_number_is_valid(account_number):
        account_number = "7810106666" + "".join(random.choices(string.digits, k=16))
    return account_number


def username_exists(username):
    with session:
        query = session.query(Users.username).filter(Users.username == username).all()
    if query:
        return True


def account_number_exists(account_number):
    with session:
        query = (
            session.query(BankAccounts.account_number)
            .filter(BankAccounts.account_number == account_number)
            .all()
        )
    if query:
        return True
    return False


class Account:
    def __init__(self) -> None:
        self.__account_id = None
        self.__is_logged = False

    @property
    def is_logged(self):
        return self.__is_logged

    @property
    def balance(self):
        with session:
            query = (
                session.query(BankAccounts.balance)
                .join(Users, Users.user_id == BankAccounts.user_id)
                .filter(Users.user_id == self.__user_id)
                .one()
            )
        return query.balance

    def __repr__(self) -> str:
        if self.is_logged:
            return "Account: " + self.__account_id + " Balance: " + str(self.balance)
        else:
            return "Account not logged"

    def login(self, username: str, password: str) -> bool:
        with session:
            # Get query data of username
            query = (
                session.query(Users, Owners.first_name, Owners.last_name)
                .join(Owners, Owners.owner_id == Users.owner_id)
                .filter(Users.username == username)
                .one()
            )

            # If password match, login to account
            if query and query.Users.check_password(password):
                now = datetime.now()
                self.__user_id = query.Users.user_id
                self.__is_logged = True
                print(
                    f"Welcome {query.first_name} {query.last_name}\nYour balance is: ${self.balance}"
                )

                # Update query with the last successful login
                if query.Users.last_ok_login:
                    print(
                        f"Your previous successful login: {query.Users.last_ok_login}"
                    )
                    session.commit()

                # Update query with the last unsuccessful login
                if query.Users.last_nok_login:
                    print(
                        f"Your previous unsuccessful login: {query.Users.last_nok_login}"
                    )
                    session.commit()
                logging.info(f"Successful login, username: {username}")
                return True

            # If login was not successful, add timestamp to aware the owner
            elif query:
                query.Users.last_nok_login = now
                session.commit()
        print("Invalid user or password")
        logging.info(f"Unsuccessful login, username: {username}")
        return False

    def logout(self):
        # Clear the class instance atributes
        self.__user_id = None
        self.__is_logged = False

    def modify_account(self):
        # Read all inputs to change the account data
        try:
            new_first_name = get_valid_input(
                "New first name (leave blank to keep current): "
            )
            new_last_name = get_valid_input(
                "New last name (leave blank to keep current): "
            )
            new_email = get_valid_input(
                "New email (leave blank to keep current): ", email_is_valid
            )
            new_phone_number = get_valid_input(
                "New phone number (leave blank to keep current): ", phone_is_valid
            )
            new_password = get_valid_input(
                "New password (leave blank to keep current): ", password_is_valid
            )
        except ValueError as e:
            print(str(e))
            return

        with session:
            # Retrieve the user's account information
            user = session.query(Users).filter(Users.user_id == self.__user_id).one()

            owner = user.owner

            # Update the owner information if new values are provided
            if new_first_name:
                owner.first_name = new_first_name
            if new_last_name:
                owner.last_name = new_last_name
            if new_email:
                owner.email = new_email
            if new_phone_number:
                owner.phone_number = new_phone_number

            # Update the user password if a new password is provided
            if new_password:
                user.set_password(password=new_password)

            # Commit the changes to the database
            session.commit()
        clear()
        logging.info(f"Updated account details, account_id: {self.__account_id}")
        print("Account successfully updated")

    def display_bank_account_details(self):
        # Check if account is logged
        if not self.is_logged:
            raise bankAccountExceptions.AccountNotLoggedException(
                "You need to login first before performing any actions"
            )

        # Perform sql query
        with session:
            query = (
                session.query(BankAccounts)
                .join(Users, Users.user_id == BankAccounts.user_id)
                .filter(Users.user_id == self.__user_id)
                .one()
            )

        # Output results of bank account (query)
        print(
            f"Card number: {query.account_number}\nBalance: ${query.balance}\nStatus: {query.status}\nCreated at: {query.created_at}"
        )

    def display_all_transactions(self):
        # Check if account is logged
        if not self.is_logged:
            raise bankAccountExceptions.AccountNotLoggedException(
                "You need to login first before performing any actions"
            )

        # Perform sql query
        with session:
            query = (
                session.query(Transactions, TransactionTypes.type)
                .join(
                    BankAccounts,
                    BankAccounts.bank_account_id == Transactions.bank_account_id,
                )
                .join(Users, Users.user_id == BankAccounts.user_id)
                .join(
                    TransactionTypes,
                    TransactionTypes.transaction_type_id
                    == Transactions.transaction_type_id,
                )
                .filter(Users.user_id == self.__user_id)
                .order_by(Transactions.timestamp.desc())
                .all()
            )

        # Output transactions if any
        if not query:
            print("No transactions found.")
        for idx, row in enumerate(iterable=query, start=1):
            print(
                f"{idx}) Transaction: {row.type}\tAmount: ${row.Transactions.amount}\tBalance before: ${row.Transactions.balance_before}\tDate: {row.Transactions.timestamp}"
            )

    def deposit(self, amount: float):
        TRANSACTION_TYPE_ID = 1

        # Check if account is logged
        if not self.is_logged:
            raise bankAccountExceptions.AccountNotLoggedException(
                "You need to login first before performing any actions"
            )

        # Basic check for deposit amount
        if not isinstance(amount, (int, float)):
            raise TypeError("Deposit amount must be decimal")
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than 0$")

        # Perform query
        with session:
            query = (
                session.query(BankAccounts)
                .join(Users, Users.user_id == BankAccounts.user_id)
                .filter(Users.user_id == self.__user_id)
                .one()
            )
            transaction = Transactions(
                transaction_type_id=TRANSACTION_TYPE_ID,
                timestamp=datetime.now(),
                amount=amount,
                balance_before=query.balance,
                balance_after=query.balance + amount,
                description="deposit",
                bank_account_id=query.bank_account_id,
            )
            query.balance += amount
            session.add(transaction)
            session.commit()
        logging.info(f"Account_id: {self.__account_id} performed deposit for ${amount}")
        print(f"Successfully deposited ${amount}")

    def withdraw(self, amount: float):
        TRANSACTION_TYPE_ID = 2

        # Check if account is logged
        if not self.is_logged:
            raise bankAccountExceptions.AccountNotLoggedException(
                "You need to login first before performing any actions"
            )

        # Basic check for withdraw amount
        if not isinstance(amount, (int, float)):
            raise TypeError("Withdrawal amount must be decimal")
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero")
        if amount > self.balance:
            raise ValueError("Withdrawal amount must be lower or equal to balance")

        # Perform query
        with session:
            query = (
                session.query(BankAccounts)
                .join(Users, Users.user_id == BankAccounts.user_id)
                .filter(Users.user_id == self.__user_id)
                .one()
            )

            transaction = Transactions(
                transaction_type_id=TRANSACTION_TYPE_ID,
                timestamp=datetime.now(),
                amount=amount,
                balance_before=query.balance,
                balance_after=query.balance - amount,
                description="withdraw",
                bank_account_id=query.bank_account_id,
            )
            query.balance -= amount
            session.add(transaction)
            session.commit()
        logging.info(
            f"Account_id: {self.__account_id} performed withdraw for ${amount}"
        )
        print(f"Successfully withdrawed ${amount}")

    def _check_if_account_logged(self):
        # Check if account is logged
        if not self.is_logged:
            raise bankAccountExceptions.AccountNotLoggedException(
                "You need to login first before performing any actions"
            )

    def _check_outgoing_amount(self, amount):
        # Basic check for transfer amount
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be decimal")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if amount > self.balance:
            raise ValueError("Amount must be lower or equal to balance")

    def transfer_to_username(self, username: str, amount: float, description=""):
        TRANSACTION_TYPE_ID = 3

        # Perform basic checks
        self._check_if_account_logged()
        self._check_outgoing_amount(amount=amount)

        # Check if username exists
        if not username_exists(username=username):
            raise bankAccountExceptions.AccountUsernameNotFound(
                "Account username does not exist."
            )

        # Perform query
        with session:
            # Query of transaction sender (self)
            sender_query = (
                session.query(BankAccounts)
                .join(Users, Users.user_id == BankAccounts.user_id)
                .filter(Users.user_id == self.__user_id)
                .one()
            )

            # Query of transaction receipt (other)
            recipient_query = (
                session.query(BankAccounts)
                .join(Users, Users.user_id == BankAccounts.user_id)
                .filter(Users.username == username)
                .one()
            )

            # change balance of sender and recipient
            recipient_query.balance -= amount
            recipient_query.balance += amount

            now = datetime.now()

            # Create new transfer history (sender)
            sender_transaction = Transactions(
                transaction_type_id=TRANSACTION_TYPE_ID,
                timestamp=now,
                amount=amount,
                balance_before=sender_query.balance + amount,
                balance_after=sender_query.balance,
                description=description,
                bank_account_id=sender_query.bank_account_id,
            )

            # Create new transfer history (recipient)
            recipient_transaction = Transactions(
                transaction_type_id=TRANSACTION_TYPE_ID,
                timestamp=now,
                amount=amount,
                balance_before=recipient_query.balance - amount,
                balance_after=recipient_query.balance,
                description=description,
                bank_account_id=recipient_query.bank_account_id,
            )

            # Add transaction histories and commit changes
            session.add_all([sender_transaction, recipient_transaction])
            session.commit()
        logging.info(
            f"Account_id: {self.__account_id} transfered ${amount} to {username}"
        )
        print(f"Successfully transfered ${amount} to {username}")

    def transfer_to_account_number(
        self, account_number: str, amount: float, description=""
    ):
        TRANSACTION_TYPE_ID = 3

        # Perform basic checks
        self._check_if_account_logged()
        self._check_outgoing_amount(amount=amount)

        # Perform query
        with session:
            # Query of Transaction sender (self)
            sender_query = (
                session.query(BankAccounts)
                .join(Users, Users.user_id == BankAccounts.user_id)
                .filter(Users.user_id == self.__user_id)
                .one()
            )

            # change sender balance
            sender_query.balance -= amount

            now = datetime.datetime.now()

            # Create new transfer history (self)
            sender_transaction = Transactions(
                transaction_type_id=TRANSACTION_TYPE_ID,
                timestamp=now,
                amount=amount,
                balance_before=sender_query.balance,
                balance_after=sender_query.balance - amount,
                description=description,
                bank_account_id=sender_query.bank_account_id,
            )
            session.add(sender_transaction)
            session.commit()

            # Check if account number belongs to the same bank
            if account_number_exists(account_number=account_number):
                # Query of transaction receipt (other)
                recipient_query = (
                    session.query(BankAccounts)
                    .filter(BankAccounts.account_number == account_number)
                    .one()
                )
                # Create new transfer history (other)
                recipient_transaction = Transactions(
                    transaction_type_id=TRANSACTION_TYPE_ID,
                    timestamp=now,
                    amount=amount,
                    balance_before=recipient_query.balance,
                    balance_after=recipient_query.balance + amount,
                    description=description,
                    bank_account_id=recipient_query.bank_account_id,
                )
                # Change other balance + add transaction
                recipient_query.balance += amount
                session.add(recipient_transaction)

                session.commit()  # commit the session here
        logging.info(
            f"Account_id: {self.__account_id} transfered ${amount} to {account_number}"
        )
        print(f"Successfully transferred ${amount} to {account_number}")
