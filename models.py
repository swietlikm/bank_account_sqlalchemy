import bcrypt
from setup import create_engine

from sqlalchemy import TIMESTAMP, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
engine = create_engine()


class Owners(Base):
    __tablename__ = "owners"
    owner_id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False, unique=True)
    ssn = Column(String(15), nullable=False, unique=True)

class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(50), unique=True)
    password_hash = Column(String(128), nullable=False)
    owner_id = Column(Integer, ForeignKey("owners.owner_id"), nullable=False)
    last_ok_login = Column(TIMESTAMP)
    last_nok_login = Column(TIMESTAMP)

    def set_password(self, password):
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode("utf-8")

    def check_password(self, password):
        password_bytes = password.encode("utf-8")
        hashed_bytes = self.password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    owner = relationship("Owners", backref="users")

class BankAccounts(Base):
    __tablename__ = "bank_accounts"

    bank_account_id = Column(Integer, primary_key=True)
    balance = Column(Float(precision=2), nullable=False)
    account_number = Column(String(26), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    closed_at = Column(TIMESTAMP)

    user = relationship("Users", backref="bank_accounts")


class Transactions(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True)
    transaction_type_id = Column(
        Integer, ForeignKey("transaction_types.transaction_type_id"), nullable=False
    )
    timestamp = Column(TIMESTAMP, nullable=False)
    amount = Column(Float(precision=2), nullable=False)
    balance_before = Column(Float(precision=2), nullable=False)
    balance_after = Column(Float(precision=2), nullable=False)
    description = Column(String(100))
    bank_account_id = Column(
        Integer, ForeignKey("bank_accounts.bank_account_id"), nullable=False
    )

    bank_account = relationship("BankAccounts", backref="transactions")
    transaction_type = relationship("TransactionTypes", backref="transactions")


class TransactionTypes(Base):
    __tablename__ = "transaction_types"
    transaction_type_id = Column(Integer, primary_key=True)
    type = Column(String(50), nullable=False, unique=True)


Base.metadata.create_all(engine)
