from models import TransactionTypes
from setup import create_engine
from sqlalchemy.orm import Session

engine = create_engine()

with Session(engine) as session:
    try:
        # Add transaction_types
        transaction_types = ["deposit", "withdraw", "transfer"]
        for idx, transaction_type in enumerate(iterable=transaction_types, start=1):
            trans_type_row = TransactionTypes(
                transaction_type_id=idx, type=transaction_type
            )

            session.add(trans_type_row)
        session.commit()
    except:
        pass
